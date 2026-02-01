"""
Tests for the config loader module
"""
import json
import os
import tempfile
from unittest.mock import patch

import pytest

from config_loader import (
    substitute_env_vars,
    load_secrets,
    load_config,
    create_secrets_template,
    ENV_PATTERN
)


class TestEnvVarSubstitution:
    """Tests for environment variable substitution"""

    def test_substitute_simple_string(self):
        """Test substitution in a simple string"""
        with patch.dict(os.environ, {'TEST_VAR': 'test_value'}):
            result = substitute_env_vars('${TEST_VAR}')
            assert result == 'test_value'

    def test_substitute_partial_string(self):
        """Test partial substitution in a string"""
        with patch.dict(os.environ, {'API_KEY': 'abc123'}):
            result = substitute_env_vars('Bearer ${API_KEY}')
            assert result == 'Bearer abc123'

    def test_substitute_multiple_vars(self):
        """Test multiple variable substitution"""
        with patch.dict(os.environ, {'USER': 'john', 'HOST': 'localhost'}):
            result = substitute_env_vars('${USER}@${HOST}')
            assert result == 'john@localhost'

    def test_substitute_missing_var_returns_original(self):
        """Test that missing vars return original pattern"""
        # Ensure var doesn't exist
        os.environ.pop('NONEXISTENT_VAR', None)

        result = substitute_env_vars('${NONEXISTENT_VAR}')
        assert result == '${NONEXISTENT_VAR}'

    def test_substitute_in_dict(self):
        """Test substitution in dictionary values"""
        with patch.dict(os.environ, {'API_KEY': 'secret123'}):
            config = {
                'key': '${API_KEY}',
                'static': 'unchanged'
            }
            result = substitute_env_vars(config)

            assert result['key'] == 'secret123'
            assert result['static'] == 'unchanged'

    def test_substitute_in_nested_dict(self):
        """Test substitution in nested dictionaries"""
        with patch.dict(os.environ, {'KEY': 'value'}):
            config = {
                'level1': {
                    'level2': {
                        'var': '${KEY}'
                    }
                }
            }
            result = substitute_env_vars(config)

            assert result['level1']['level2']['var'] == 'value'

    def test_substitute_in_list(self):
        """Test substitution in list values"""
        with patch.dict(os.environ, {'VAR1': 'a', 'VAR2': 'b'}):
            config = ['${VAR1}', '${VAR2}', 'static']
            result = substitute_env_vars(config)

            assert result == ['a', 'b', 'static']

    def test_substitute_non_string_unchanged(self):
        """Test that non-string values are unchanged"""
        result = substitute_env_vars(12345)
        assert result == 12345

        result = substitute_env_vars(True)
        assert result is True

        result = substitute_env_vars(None)
        assert result is None


class TestLoadSecrets:
    """Tests for secrets loading"""

    def test_load_secrets_from_file(self):
        """Test loading secrets from a JSON file"""
        secrets = {
            'API_KEY': 'secret_key',
            'API_SECRET': 'secret_secret'
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(secrets, f)
            secrets_path = f.name

        try:
            loaded = load_secrets(secrets_path)
            assert loaded['API_KEY'] == 'secret_key'
            assert loaded['API_SECRET'] == 'secret_secret'
        finally:
            os.remove(secrets_path)

    def test_load_secrets_nonexistent_file(self):
        """Test loading secrets from non-existent file returns empty dict"""
        result = load_secrets('/nonexistent/path/secrets.json')
        assert result == {}

    def test_load_secrets_invalid_json(self):
        """Test loading invalid JSON returns empty dict"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('not valid json')
            path = f.name

        try:
            result = load_secrets(path)
            assert result == {}
        finally:
            os.remove(path)


class TestLoadConfig:
    """Tests for config loading"""

    def test_load_config_basic(self, sample_config):
        """Test basic config loading"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(sample_config, f)
            config_path = f.name

        try:
            loaded = load_config(config_path)

            assert loaded['broker']['adapter'] == 'etrade'
            assert loaded['trading']['initialCapital'] == 50000
        finally:
            os.remove(config_path)

    def test_load_config_with_env_substitution(self):
        """Test config loading with environment variable substitution"""
        config = {
            'broker': {
                'credentials': {
                    'apiKey': '${TEST_API_KEY}',
                    'apiSecret': '${TEST_API_SECRET}'
                }
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config, f)
            config_path = f.name

        try:
            with patch.dict(os.environ, {
                'TEST_API_KEY': 'loaded_key',
                'TEST_API_SECRET': 'loaded_secret'
            }):
                loaded = load_config(config_path)

                assert loaded['broker']['credentials']['apiKey'] == 'loaded_key'
                assert loaded['broker']['credentials']['apiSecret'] == 'loaded_secret'
        finally:
            os.remove(config_path)

    def test_load_config_removes_comments(self):
        """Test that comment fields (starting with _) are removed"""
        config = {
            '_comment': 'This is a comment',
            'broker': {
                '_note': 'Another comment',
                'adapter': 'etrade'
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config, f)
            config_path = f.name

        try:
            loaded = load_config(config_path)

            assert '_comment' not in loaded
            assert '_note' not in loaded['broker']
            assert loaded['broker']['adapter'] == 'etrade'
        finally:
            os.remove(config_path)

    def test_load_config_nonexistent_file(self):
        """Test loading non-existent config raises FileNotFoundError"""
        with pytest.raises(FileNotFoundError):
            load_config('/nonexistent/config.json')

    def test_load_config_uses_template_fallback(self, sample_config):
        """Test that template is used if config doesn't exist"""
        with tempfile.TemporaryDirectory() as tmpdir:
            template_path = os.path.join(tmpdir, 'config.template.json')
            config_path = os.path.join(tmpdir, 'config.json')

            # Create only template
            with open(template_path, 'w') as f:
                json.dump(sample_config, f)

            # Should fall back to template
            loaded = load_config(config_path)
            assert loaded['broker']['adapter'] == 'etrade'


class TestCreateSecretsTemplate:
    """Tests for secrets template creation"""

    def test_create_secrets_template(self):
        """Test creating secrets template"""
        template = create_secrets_template()

        assert '_instructions' in template
        assert 'BROKER_API_KEY' in template
        assert 'BROKER_API_SECRET' in template
        assert 'BROKER_ACCOUNT_ID' in template
        assert 'TELEGRAM_BOT_TOKEN' in template
        assert 'TELEGRAM_CHAT_ID' in template


class TestEnvPattern:
    """Tests for the environment variable regex pattern"""

    def test_env_pattern_matches_valid(self):
        """Test pattern matches valid env var syntax"""
        assert ENV_PATTERN.fullmatch('${VAR_NAME}')
        assert ENV_PATTERN.fullmatch('${SOME_VAR_123}')
        assert ENV_PATTERN.fullmatch('${a}')

    def test_env_pattern_no_match_invalid(self):
        """Test pattern doesn't match invalid syntax"""
        assert not ENV_PATTERN.fullmatch('$VAR')
        assert not ENV_PATTERN.fullmatch('${VAR')
        assert not ENV_PATTERN.fullmatch('VAR}')
        assert not ENV_PATTERN.fullmatch('plain_text')

    def test_env_pattern_findall(self):
        """Test finding multiple env vars in string"""
        text = '${VAR1} and ${VAR2} with ${VAR3}'
        matches = ENV_PATTERN.findall(text)
        assert matches == ['VAR1', 'VAR2', 'VAR3']
