#!/usr/bin/env python3
"""
Tests for the Testing Crew itself
Meta-testing: testing the test generator
"""

import unittest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestConfigFiles(unittest.TestCase):
    """Test that configuration files are valid"""

    def setUp(self):
        self.config_dir = Path(__file__).parent.parent / "config"

    def test_agents_yaml_exists(self):
        """agents.yaml file exists"""
        agents_path = self.config_dir / "agents.yaml"
        self.assertTrue(agents_path.exists(), "agents.yaml not found")

    def test_tasks_yaml_exists(self):
        """tasks.yaml file exists"""
        tasks_path = self.config_dir / "tasks.yaml"
        self.assertTrue(tasks_path.exists(), "tasks.yaml not found")

    def test_agents_yaml_valid(self):
        """agents.yaml is valid YAML"""
        import yaml

        agents_path = self.config_dir / "agents.yaml"
        with open(agents_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        self.assertIsInstance(config, dict)
        self.assertIn("qa_test_agent", config)
        self.assertIn("code_analyzer_agent", config)
        self.assertIn("test_validator_agent", config)

    def test_tasks_yaml_valid(self):
        """tasks.yaml is valid YAML"""
        import yaml

        tasks_path = self.config_dir / "tasks.yaml"
        with open(tasks_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        self.assertIsInstance(config, dict)
        self.assertIn("analyze_code_task", config)
        self.assertIn("write_tests_task", config)
        self.assertIn("validate_tests_task", config)

    def test_agents_have_required_fields(self):
        """Each agent has role, goal, backstory"""
        import yaml

        agents_path = self.config_dir / "agents.yaml"
        with open(agents_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        required_fields = ["role", "goal", "backstory"]

        for agent_name, agent_config in config.items():
            for field in required_fields:
                self.assertIn(
                    field, agent_config,
                    f"Agent '{agent_name}' missing required field: {field}"
                )

    def test_tasks_have_required_fields(self):
        """Each task has description and expected_output"""
        import yaml

        tasks_path = self.config_dir / "tasks.yaml"
        with open(tasks_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        required_fields = ["description", "expected_output"]

        for task_name, task_config in config.items():
            for field in required_fields:
                self.assertIn(
                    field, task_config,
                    f"Task '{task_name}' missing required field: {field}"
                )


class TestToolsModule(unittest.TestCase):
    """Test custom tools"""

    @classmethod
    def setUpClass(cls):
        """Check if CrewAI is available for tools"""
        try:
            import crewai
        except ImportError:
            raise unittest.SkipTest("CrewAI not installed - skipping tools tests")

    def test_coverage_tool_import(self):
        """CoverageTool can be imported"""
        from tools.coverage_tool import CoverageTool
        self.assertTrue(True)

    def test_syntax_checker_tool_import(self):
        """SyntaxCheckerTool can be imported"""
        from tools.coverage_tool import SyntaxCheckerTool
        self.assertTrue(True)

    def test_syntax_checker_valid_code(self):
        """SyntaxCheckerTool validates correct Python code"""
        from tools.coverage_tool import SyntaxCheckerTool
        import json

        tool = SyntaxCheckerTool()
        result = json.loads(tool._run("def foo(): return 42"))

        self.assertTrue(result["valid"])

    def test_syntax_checker_invalid_code(self):
        """SyntaxCheckerTool detects syntax errors"""
        from tools.coverage_tool import SyntaxCheckerTool
        import json

        tool = SyntaxCheckerTool()
        result = json.loads(tool._run("def foo( return 42"))

        self.assertFalse(result["valid"])
        self.assertIn("error", result)


class TestMainModule(unittest.TestCase):
    """Test main.py entry point"""

    def test_main_import(self):
        """main.py can be imported"""
        try:
            from main import main, parse_args, create_example_file
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Failed to import main: {e}")

    def test_create_example_file(self):
        """create_example_file creates a valid Python file"""
        from main import create_example_file

        path = create_example_file()
        self.assertTrue(Path(path).exists())

        # Verify it's valid Python
        with open(path, 'r') as f:
            code = f.read()

        try:
            compile(code, path, "exec")
        except SyntaxError as e:
            self.fail(f"Example file has syntax error: {e}")

    def test_parse_args_defaults(self):
        """parse_args returns correct defaults"""
        from main import parse_args

        with patch('sys.argv', ['main.py', 'test.py']):
            args = parse_args()

        self.assertEqual(args.file_path, 'test.py')
        self.assertEqual(args.type, 'unit')
        self.assertEqual(args.framework, 'pytest')
        self.assertEqual(args.language, 'python')


class TestCrewModule(unittest.TestCase):
    """Test crew.py (with mocked CrewAI)"""

    @classmethod
    def setUpClass(cls):
        """Check if CrewAI is available"""
        try:
            import crewai
        except ImportError:
            raise unittest.SkipTest("CrewAI not installed - skipping crew tests")

    def test_crew_initialization(self):
        """TestingCrew initializes without errors"""
        from crew import TestingCrew
        crew = TestingCrew()
        self.assertIsNotNone(crew)


class TestIntegration(unittest.TestCase):
    """Integration tests (skipped if CrewAI not installed)"""

    @classmethod
    def setUpClass(cls):
        """Check if CrewAI is available"""
        try:
            import crewai
        except ImportError:
            raise unittest.SkipTest("CrewAI not installed - skipping integration tests")

    def test_full_pipeline_dry_run(self):
        """Test full pipeline with mocked LLM"""
        # This would require API keys, so we skip in CI
        self.skipTest("Requires API keys - run manually")


def run_tests():
    """Run all tests"""
    print("=" * 60)
    print("🧪 Testing Agent - Self Tests")
    print("=" * 60)

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestConfigFiles))
    suite.addTests(loader.loadTestsFromTestCase(TestToolsModule))
    suite.addTests(loader.loadTestsFromTestCase(TestMainModule))
    suite.addTests(loader.loadTestsFromTestCase(TestCrewModule))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 60)
    print(f"📊 Results: {result.testsRun} tests, "
          f"{len(result.failures)} failures, "
          f"{len(result.errors)} errors, "
          f"{len(result.skipped)} skipped")
    print("=" * 60)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
