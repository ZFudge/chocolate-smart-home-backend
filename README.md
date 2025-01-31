# Chocolate Smart Home Backend

A modern, extensible smart home backend system built with FastAPI, featuring real-time communication and plugin-based device management.

## Overview

This backend service provides a bridge between the [Chocolate Smart Home Frontend](https://github.com/ZFudge/chocolate-smart-home-frontend) and [IoT microcontrollers](https://github.com/ZFudge/chocolate-smart-home-microcontrollers), offering:
- Real-time WebSocket communication with frontend clients
- MQTT-based device communication
- Plugin-based architecture for device integration
- Optional PostgreSQL persistence for device configurations

## Technology Stack

- **FastAPI** - High-performance web framework
- **MQTT** - IoT device communication protocol
- **WebSocket** - Real-time frontend communication
- **PostgreSQL** - Optional persistent storage
- **SQLAlchemy** - ORM for database operations
- **PyTest** - Testing framework

## Architecture

### Plugin System
Device plugins are modular components located in `src/plugins/device_plugins/`. Each plugin provides:
- A duplex messenger for server-device data translation
- A device manager for database interactions
- Optional models for persistent configuration
- Data schemas for both server and controller interfaces

### Device Requirements

All microcontrollers must provide:
- Unique MQTT ID for isolated communication
- Device type identifier for plugin selection
- Display name for the user interface

### Database

The PostgreSQL database is optional and supports:
- Device configuration persistence
- Custom device naming
- Device tagging
- User-defined parameter storage
