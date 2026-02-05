"""
Testing Crew - AI-powered test generation system
Built on CrewAI framework

Usage:
    from crew import TestingCrew
    crew = TestingCrew()
    result = crew.run(file_path="src/calculator.py")
"""

import os
from pathlib import Path
from crewai import Agent, Task, Crew, Process
from crewai.project import CrewBase, agent, task, crew
from crewai_tools import FileReadTool

# Путь к конфигам относительно этого файла
CONFIG_DIR = Path(__file__).parent.parent / "config"


@CrewBase
class TestingCrew:
    """
    Crew для автоматизированного тестирования кода.

    Архитектура: Sequential Pipeline
    1. Analyze → 2. Write Tests → 3. Validate → 4. Fix (if needed)

    Принципы:
    - Узкая специализация агентов
    - 80% усилий на дизайн задач
    - Safe code execution (Docker)
    """

    agents_config = str(CONFIG_DIR / "agents.yaml")
    tasks_config = str(CONFIG_DIR / "tasks.yaml")

    def __init__(self):
        """Инициализация crew с загрузкой конфигов"""
        self._load_configs()

    def _load_configs(self):
        """Загрузка YAML конфигураций"""
        import yaml

        with open(self.agents_config, 'r', encoding='utf-8') as f:
            self._agents_config = yaml.safe_load(f)

        with open(self.tasks_config, 'r', encoding='utf-8') as f:
            self._tasks_config = yaml.safe_load(f)

    # ==================== AGENTS ====================

    @agent
    def code_analyzer_agent(self) -> Agent:
        """Агент для анализа кода"""
        config = self._agents_config["code_analyzer_agent"]
        return Agent(
            role=config["role"],
            goal=config["goal"],
            backstory=config["backstory"],
            tools=[FileReadTool()],
            verbose=True,
            allow_delegation=False,
            max_iter=10,
            respect_context_window=True,
            cache=True
        )

    @agent
    def qa_test_agent(self) -> Agent:
        """Главный агент для написания тестов"""
        config = self._agents_config["qa_test_agent"]
        return Agent(
            role=config["role"],
            goal=config["goal"],
            backstory=config["backstory"],
            tools=[FileReadTool()],
            verbose=True,
            allow_delegation=False,
            allow_code_execution=True,
            code_execution_mode="safe",  # Docker sandbox
            max_iter=15,
            max_execution_time=300,  # 5 минут максимум
            respect_context_window=True,
            cache=True
        )

    @agent
    def test_validator_agent(self) -> Agent:
        """Агент для валидации тестов"""
        config = self._agents_config["test_validator_agent"]
        return Agent(
            role=config["role"],
            goal=config["goal"],
            backstory=config["backstory"],
            tools=[],  # Валидатору не нужны внешние инструменты
            verbose=True,
            allow_delegation=False,
            max_iter=10,
            respect_context_window=True,
            cache=True
        )

    # ==================== TASKS ====================

    @task
    def analyze_code_task(self) -> Task:
        """Задача анализа кода"""
        config = self._tasks_config["analyze_code_task"]
        return Task(
            description=config["description"],
            expected_output=config["expected_output"],
            agent=self.code_analyzer_agent()
        )

    @task
    def write_tests_task(self) -> Task:
        """Задача написания тестов"""
        config = self._tasks_config["write_tests_task"]
        return Task(
            description=config["description"],
            expected_output=config["expected_output"],
            agent=self.qa_test_agent(),
            context=[self.analyze_code_task()]  # Зависит от анализа
        )

    @task
    def validate_tests_task(self) -> Task:
        """Задача валидации тестов"""
        config = self._tasks_config["validate_tests_task"]
        return Task(
            description=config["description"],
            expected_output=config["expected_output"],
            agent=self.test_validator_agent(),
            context=[self.write_tests_task()]  # Зависит от написанных тестов
        )

    # ==================== CREW ====================

    @crew
    def crew(self) -> Crew:
        """Собираем crew с sequential процессом"""
        return Crew(
            agents=[
                self.code_analyzer_agent(),
                self.qa_test_agent(),
                self.test_validator_agent()
            ],
            tasks=[
                self.analyze_code_task(),
                self.write_tests_task(),
                self.validate_tests_task()
            ],
            process=Process.sequential,  # Pipeline
            verbose=True,
            memory=True,  # Сохранять контекст между задачами
            max_rpm=10,   # Rate limiting
            planning=True,  # Планирование перед выполнением
            planning_llm="gpt-4o-mini"  # Легкая модель для планирования
        )

    # ==================== RUN METHODS ====================

    def run(
        self,
        file_path: str,
        test_type: str = "unit",
        test_framework: str = "pytest",
        language: str = "python"
    ) -> dict:
        """
        Запуск тестирования для файла.

        Args:
            file_path: Путь к файлу для тестирования
            test_type: Тип тестов (unit, integration, e2e)
            test_framework: Фреймворк (pytest, unittest, jest)
            language: Язык программирования

        Returns:
            dict с результатами: analysis, tests, validation
        """
        # Читаем код
        with open(file_path, 'r', encoding='utf-8') as f:
            code_content = f.read()

        # Входные данные для crew
        inputs = {
            "file_path": file_path,
            "code_content": code_content,
            "test_type": test_type,
            "test_framework": test_framework,
            "language": language
        }

        # Запуск
        result = self.crew().kickoff(inputs=inputs)

        return {
            "raw": result.raw,
            "tasks_output": [task.raw for task in result.tasks_output] if hasattr(result, 'tasks_output') else [],
            "token_usage": result.token_usage if hasattr(result, 'token_usage') else None
        }

    def run_and_save(
        self,
        file_path: str,
        output_path: str = None,
        **kwargs
    ) -> str:
        """
        Запуск тестирования и сохранение результата в файл.

        Args:
            file_path: Путь к файлу для тестирования
            output_path: Путь для сохранения тестов (auto если None)
            **kwargs: Дополнительные параметры для run()

        Returns:
            Путь к сохранённому файлу с тестами
        """
        result = self.run(file_path, **kwargs)

        # Автоматический путь: src/calc.py → tests/test_calc.py
        if output_path is None:
            base_name = Path(file_path).stem
            output_path = f"tests/test_{base_name}.py"

        # Создаём директорию если нужно
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        # Извлекаем тесты из результата
        tests_content = result["raw"]

        # Если результат содержит markdown code blocks, извлекаем код
        if "```python" in tests_content:
            import re
            code_blocks = re.findall(r'```python\n(.*?)```', tests_content, re.DOTALL)
            if code_blocks:
                tests_content = code_blocks[-1]  # Берём последний блок (обычно финальные тесты)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(tests_content)

        print(f"✅ Tests saved to: {output_path}")
        return output_path


# Для использования без CrewBase декоратора
def create_testing_crew() -> TestingCrew:
    """Factory function для создания TestingCrew"""
    return TestingCrew()
