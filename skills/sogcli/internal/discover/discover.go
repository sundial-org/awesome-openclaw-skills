// Package discover provides email server auto-discovery.
package discover

import (
	"fmt"
	"net"
	"strings"
)

// ServerConfig holds discovered server settings.
type ServerConfig struct {
	Host string
	Port int
}

// Result holds the discovered IMAP and SMTP settings.
type Result struct {
	IMAP *ServerConfig
	SMTP *ServerConfig
}

// Discover attempts to find IMAP and SMTP servers for an email domain.
// It tries SRV records first, then falls back to common hostnames.
func Discover(email string) (*Result, error) {
	parts := strings.Split(email, "@")
	if len(parts) != 2 {
		return nil, fmt.Errorf("invalid email address: %s", email)
	}
	domain := parts[1]

	result := &Result{}

	// Try IMAP SRV records
	if srv := lookupSRV("imaps", "tcp", domain); srv != nil {
		result.IMAP = srv
	} else if srv := lookupSRV("imap", "tcp", domain); srv != nil {
		result.IMAP = srv
	}

	// Try SMTP SRV records
	if srv := lookupSRV("submission", "tcp", domain); srv != nil {
		result.SMTP = srv
	} else if srv := lookupSRV("smtp", "tcp", domain); srv != nil {
		result.SMTP = srv
	}

	// Fall back to common hostnames
	if result.IMAP == nil {
		result.IMAP = tryCommonHosts(domain, []string{
			"imap.%s",
			"mail.%s",
			"imap.mail.%s",
		}, 993)
	}

	if result.SMTP == nil {
		result.SMTP = tryCommonHosts(domain, []string{
			"smtp.%s",
			"mail.%s",
			"smtp.mail.%s",
		}, 587)
	}

	// Check for well-known providers
	result = applyWellKnownProviders(domain, result)

	if result.IMAP == nil && result.SMTP == nil {
		return nil, fmt.Errorf("could not discover servers for %s", domain)
	}

	return result, nil
}

func lookupSRV(service, proto, domain string) *ServerConfig {
	_, addrs, err := net.LookupSRV(service, proto, domain)
	if err != nil || len(addrs) == 0 {
		return nil
	}

	// Use the highest priority (lowest number) server
	srv := addrs[0]
	return &ServerConfig{
		Host: strings.TrimSuffix(srv.Target, "."),
		Port: int(srv.Port),
	}
}

func tryCommonHosts(domain string, patterns []string, defaultPort int) *ServerConfig {
	for _, pattern := range patterns {
		host := fmt.Sprintf(pattern, domain)
		if _, err := net.LookupHost(host); err == nil {
			return &ServerConfig{
				Host: host,
				Port: defaultPort,
			}
		}
	}
	return nil
}

func applyWellKnownProviders(domain string, result *Result) *Result {
	// Google Workspace / Gmail
	if isGoogleDomain(domain) {
		if result.IMAP == nil {
			result.IMAP = &ServerConfig{Host: "imap.gmail.com", Port: 993}
		}
		if result.SMTP == nil {
			result.SMTP = &ServerConfig{Host: "smtp.gmail.com", Port: 587}
		}
	}

	// Microsoft 365 / Outlook
	if isMicrosoftDomain(domain) {
		if result.IMAP == nil {
			result.IMAP = &ServerConfig{Host: "outlook.office365.com", Port: 993}
		}
		if result.SMTP == nil {
			result.SMTP = &ServerConfig{Host: "smtp.office365.com", Port: 587}
		}
	}

	return result
}

func isGoogleDomain(domain string) bool {
	// Check MX records for Google
	mxs, err := net.LookupMX(domain)
	if err != nil {
		return false
	}
	for _, mx := range mxs {
		if strings.Contains(strings.ToLower(mx.Host), "google") ||
			strings.Contains(strings.ToLower(mx.Host), "googlemail") {
			return true
		}
	}
	return domain == "gmail.com" || domain == "googlemail.com"
}

func isMicrosoftDomain(domain string) bool {
	// Check MX records for Microsoft
	mxs, err := net.LookupMX(domain)
	if err != nil {
		return false
	}
	for _, mx := range mxs {
		if strings.Contains(strings.ToLower(mx.Host), "outlook") ||
			strings.Contains(strings.ToLower(mx.Host), "microsoft") {
			return true
		}
	}
	return domain == "outlook.com" || domain == "hotmail.com" || domain == "live.com"
}
