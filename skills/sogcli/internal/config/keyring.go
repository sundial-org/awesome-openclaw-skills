package config

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"strings"

	"github.com/zalando/go-keyring"
)

const serviceName = "sog"

// StorageType represents the credential storage backend.
type StorageType string

const (
	StorageKeyring StorageType = "keychain"
	StorageFile    StorageType = "file"
)

// DefaultStorage is the default storage type.
var DefaultStorage = StorageKeyring

// CurrentStorage holds the active storage type.
var CurrentStorage = DefaultStorage

// SetStorageType sets the storage type for credentials.
func SetStorageType(st StorageType) {
	CurrentStorage = st
}

// Protocol represents a service protocol for password lookup.
type Protocol string

const (
	ProtocolDefault Protocol = ""
	ProtocolIMAP    Protocol = "imap"
	ProtocolSMTP    Protocol = "smtp"
	ProtocolCalDAV  Protocol = "caldav"
	ProtocolCardDAV Protocol = "carddav"
	ProtocolWebDAV  Protocol = "webdav"
)

// credentialsFilePath returns the path to the credentials file.
func credentialsFilePath() (string, error) {
	dir, err := configDir()
	if err != nil {
		return "", err
	}
	return filepath.Join(dir, "credentials.json"), nil
}

// FileCredentials holds credentials stored in a file.
type FileCredentials struct {
	Passwords map[string]string `json:"passwords"`
}

// loadFileCredentials loads credentials from the file.
func loadFileCredentials() (*FileCredentials, error) {
	path, err := credentialsFilePath()
	if err != nil {
		return nil, err
	}

	creds := &FileCredentials{Passwords: make(map[string]string)}

	data, err := os.ReadFile(path)
	if os.IsNotExist(err) {
		return creds, nil
	}
	if err != nil {
		return nil, fmt.Errorf("failed to read credentials: %w", err)
	}

	if err := json.Unmarshal(data, creds); err != nil {
		return nil, fmt.Errorf("failed to parse credentials: %w", err)
	}

	return creds, nil
}

// saveFileCredentials saves credentials to the file.
func saveFileCredentials(creds *FileCredentials) error {
	path, err := credentialsFilePath()
	if err != nil {
		return err
	}

	dir := filepath.Dir(path)
	if err := os.MkdirAll(dir, 0700); err != nil {
		return fmt.Errorf("failed to create config dir: %w", err)
	}

	data, err := json.MarshalIndent(creds, "", "  ")
	if err != nil {
		return fmt.Errorf("failed to marshal credentials: %w", err)
	}

	if err := os.WriteFile(path, data, 0600); err != nil {
		return fmt.Errorf("failed to write credentials: %w", err)
	}

	return nil
}

// SetPassword stores a password using the current storage type.
func SetPassword(email, password string) error {
	switch CurrentStorage {
	case StorageFile:
		return setPasswordFile(email, password)
	default:
		return setPasswordKeyring(email, password)
	}
}

// setPasswordKeyring stores a password in the system keyring.
func setPasswordKeyring(email, password string) error {
	return keyring.Set(serviceName, email, password)
}

// setPasswordFile stores a password in the credentials file.
func setPasswordFile(email, password string) error {
	creds, err := loadFileCredentials()
	if err != nil {
		return err
	}
	creds.Passwords[email] = password
	return saveFileCredentials(creds)
}

// SetPasswordForProtocol stores a protocol-specific password.
func SetPasswordForProtocol(email string, protocol Protocol, password string) error {
	if protocol == ProtocolDefault {
		return SetPassword(email, password)
	}
	key := fmt.Sprintf("%s:%s", email, protocol)
	return SetPassword(key, password)
}

// GetPassword retrieves a password using the current storage type.
// Falls back to environment variable SOG_PASSWORD_<email> if storage fails.
func GetPassword(email string) (string, error) {
	var password string
	var err error

	switch CurrentStorage {
	case StorageFile:
		password, err = getPasswordFile(email)
	default:
		password, err = getPasswordKeyring(email)
	}

	if err == nil {
		return password, nil
	}

	// Fall back to environment variable
	envKey := "SOG_PASSWORD_" + sanitizeEnvKey(email)
	if envPass := os.Getenv(envKey); envPass != "" {
		return envPass, nil
	}

	return "", fmt.Errorf("password not found for %s (tried %s and %s)", email, CurrentStorage, envKey)
}

// getPasswordKeyring retrieves a password from the system keyring.
func getPasswordKeyring(email string) (string, error) {
	return keyring.Get(serviceName, email)
}

// getPasswordFile retrieves a password from the credentials file.
func getPasswordFile(email string) (string, error) {
	creds, err := loadFileCredentials()
	if err != nil {
		return "", err
	}
	password, ok := creds.Passwords[email]
	if !ok {
		return "", fmt.Errorf("password not found in file")
	}
	return password, nil
}

// GetPasswordForProtocol retrieves a protocol-specific password.
// Falls back to: protocol-specific key → default key → environment variable.
func GetPasswordForProtocol(email string, protocol Protocol) (string, error) {
	// Try protocol-specific key first
	if protocol != ProtocolDefault {
		key := fmt.Sprintf("%s:%s", email, protocol)
		password, err := GetPassword(key)
		if err == nil {
			return password, nil
		}

		// Try protocol-specific environment variable
		envKey := fmt.Sprintf("SOG_PASSWORD_%s_%s", sanitizeEnvKey(email), strings.ToUpper(string(protocol)))
		if envPass := os.Getenv(envKey); envPass != "" {
			return envPass, nil
		}
	}

	// Fall back to default password
	return GetPassword(email)
}

// DeletePassword removes a password using the current storage type.
func DeletePassword(email string) error {
	switch CurrentStorage {
	case StorageFile:
		return deletePasswordFile(email)
	default:
		return deletePasswordKeyring(email)
	}
}

// deletePasswordKeyring removes a password from the system keyring.
func deletePasswordKeyring(email string) error {
	return keyring.Delete(serviceName, email)
}

// deletePasswordFile removes a password from the credentials file.
func deletePasswordFile(email string) error {
	creds, err := loadFileCredentials()
	if err != nil {
		return err
	}
	delete(creds.Passwords, email)
	return saveFileCredentials(creds)
}

// DeletePasswordForProtocol removes a protocol-specific password.
func DeletePasswordForProtocol(email string, protocol Protocol) error {
	if protocol == ProtocolDefault {
		return DeletePassword(email)
	}
	key := fmt.Sprintf("%s:%s", email, protocol)
	return DeletePassword(key)
}

// sanitizeEnvKey converts an email to a valid environment variable suffix.
// e.g., "user@example.com" -> "USER_EXAMPLE_COM"
func sanitizeEnvKey(email string) string {
	s := strings.ReplaceAll(email, "@", "_")
	s = strings.ReplaceAll(s, ".", "_")
	s = strings.ReplaceAll(s, "-", "_")
	return strings.ToUpper(s)
}
