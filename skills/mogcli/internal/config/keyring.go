package config

import (
	"encoding/json"
	"fmt"

	"github.com/zalando/go-keyring"
)

const (
	serviceName = "mog"
	tokenKey    = "oauth_tokens"
)

// StorageType represents the credential storage backend.
type StorageType string

const (
	StorageFile    StorageType = "file"
	StorageKeyring StorageType = "keyring"
)

// DefaultStorage is the default storage type.
var DefaultStorage = StorageFile

// CurrentStorage holds the active storage type.
var CurrentStorage = DefaultStorage

// SetStorage sets the storage type for credentials.
func SetStorage(st StorageType) {
	CurrentStorage = st
}

// SaveTokensKeyring saves OAuth tokens to the system keyring.
func SaveTokensKeyring(tokens *Tokens) error {
	data, err := json.Marshal(tokens)
	if err != nil {
		return fmt.Errorf("failed to marshal tokens: %w", err)
	}
	return keyring.Set(serviceName, tokenKey, string(data))
}

// LoadTokensKeyring loads OAuth tokens from the system keyring.
func LoadTokensKeyring() (*Tokens, error) {
	data, err := keyring.Get(serviceName, tokenKey)
	if err != nil {
		if err == keyring.ErrNotFound {
			return nil, fmt.Errorf("not logged in. Run: mog auth login")
		}
		return nil, fmt.Errorf("failed to get tokens from keyring: %w", err)
	}

	var tokens Tokens
	if err := json.Unmarshal([]byte(data), &tokens); err != nil {
		return nil, fmt.Errorf("failed to unmarshal tokens: %w", err)
	}
	return &tokens, nil
}

// DeleteTokensKeyring removes OAuth tokens from the system keyring.
func DeleteTokensKeyring() error {
	err := keyring.Delete(serviceName, tokenKey)
	if err != nil && err != keyring.ErrNotFound {
		return fmt.Errorf("failed to delete tokens from keyring: %w", err)
	}
	return nil
}

// SaveTokensAuto saves tokens using the current storage type.
func SaveTokensAuto(tokens *Tokens) error {
	switch CurrentStorage {
	case StorageKeyring:
		return SaveTokensKeyring(tokens)
	default:
		return SaveTokens(tokens)
	}
}

// LoadTokensAuto loads tokens using the current storage type.
func LoadTokensAuto() (*Tokens, error) {
	switch CurrentStorage {
	case StorageKeyring:
		return LoadTokensKeyring()
	default:
		return LoadTokens()
	}
}

// DeleteTokensAuto deletes tokens using the current storage type.
func DeleteTokensAuto() error {
	switch CurrentStorage {
	case StorageKeyring:
		return DeleteTokensKeyring()
	default:
		return DeleteTokens()
	}
}
