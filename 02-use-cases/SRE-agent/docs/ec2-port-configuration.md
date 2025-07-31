# EC2 Instance Port Configuration

## Overview

This document outlines the required port configurations for EC2 instances in the SRE Agent infrastructure. All servers use SSL encryption to ensure secure communication and data protection.

## Required Inbound Ports

### HTTPS Traffic
- **Port 443 (HTTPS)**: Primary secure web traffic
  - Protocol: TCP
  - Source: 0.0.0.0/0 (open to internet)
  - Purpose: Secure web interface and API endpoints

### Application Ports
- **Ports 8011-8014 (Custom Applications)**: Application-specific services
  - Protocol: TCP
  - Source: 0.0.0.0/0 (open to internet)
  - Purpose: Internal service communication and application endpoints

## AWS Security Group Best Practices

### Inbound Rules Configuration
- Only allow necessary ports to minimize attack surface
- All configured ports are open to internet traffic (0.0.0.0/0)
- Implement separate security groups for different service tiers
- Rely on application-level security and SSL/TLS for protection

### SSL/TLS Protection
- All services on configured ports use SSL/TLS encryption
- Certificates should be managed through AWS Certificate Manager (ACM)
- Enforce HTTPS redirects for web traffic on port 443

### Security Recommendations
- Regular security group audits and reviews
- Use descriptive names and tags for security groups
- Implement least privilege access principles
- Monitor traffic patterns and unusual access attempts
- Consider using AWS WAF for additional web application protection

## Port Usage Summary

| Port | Protocol | Purpose | SSL Required |
|------|----------|---------|--------------|
| 443  | TCP      | HTTPS Web Traffic | Yes |
| 8011 | TCP      | Application Service | Yes |
| 8012 | TCP      | Application Service | Yes |
| 8013 | TCP      | Application Service | Yes |
| 8014 | TCP      | Application Service | Yes |

## Compliance Notes

- All configured ports enforce SSL/TLS encryption
- Regular security assessments should include port configuration reviews
- Monitor and log all traffic on configured ports for security analysis 