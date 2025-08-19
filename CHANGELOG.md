# Changelog

All notable changes to the Hospitable Python SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2024-08-19

### Added
- Initial release of Hospitable Python SDK
- Complete support for Hospitable Public API v2
- Personal Access Token (PAT) authentication
- OAuth 2.0 authentication with automatic token refresh
- Comprehensive endpoint coverage:
  - Properties management (list, get, search, calendar)
  - Reservations (list, get with filtering)
  - Guest messaging (list, send)
  - Reviews (list, respond)
  - User account information
- Automatic rate limiting and retry logic
- Built-in error handling with custom exceptions
- Webhook signature verification support
- Type hints and data models
- Context manager support
- Session connection pooling
- Comprehensive documentation:
  - Quick start guide
  - Authentication guide (PAT and OAuth)
  - API reference with examples
  - Webhooks setup guide
  - Rate limiting best practices
- Example scripts and practical use cases
- Production-ready features:
  - Exponential backoff retry
  - Request timeout handling
  - Environment variable configuration
  - Proper logging and debugging support

### Technical Details
- Python 3.8+ support
- Minimal dependencies (requests only)
- Full OpenAPI 3.1 specification included
- MIT License
- Comprehensive test coverage
- GitHub Actions CI/CD ready

### API Coverage
- ✅ Properties: List, get, search with availability/pricing
- ✅ Calendar: Get and update pricing/availability  
- ✅ Reservations: List and get with includes
- ✅ Messages: List and send with rate limiting
- ✅ Reviews: List and respond
- ✅ User: Account and billing information
- ✅ Webhooks: Signature verification helpers

### Authentication
- ✅ Personal Access Tokens (PAT)
- ✅ OAuth 2.0 Authorization Code flow
- ✅ Automatic token refresh
- ✅ Environment variable configuration

### Developer Experience
- ✅ Type hints throughout
- ✅ Comprehensive error handling
- ✅ Automatic retry with exponential backoff
- ✅ Rate limit handling (1000 req/min calendar, 2/min messages)
- ✅ Session management and connection pooling
- ✅ Context manager support (`with` statements)
- ✅ Detailed documentation and examples

[Unreleased]: https://github.com/keithherrington/hospitable-python/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/keithherrington/hospitable-python/releases/tag/v0.1.0