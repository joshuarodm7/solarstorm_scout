#!/bin/bash
# SolarStorm Scout - systemd Uninstallation Script

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}╔════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║    🌞 SolarStorm Scout Uninstaller 🌞     ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════╝${NC}"
echo ""

# Check if service exists
if ! sudo systemctl list-units --full --all | grep -q "solarstorm-scout.service"; then
    echo -e "${YELLOW}SolarStorm Scout service not found${NC}"
    echo "Nothing to uninstall."
    exit 0
fi

echo "This will remove SolarStorm Scout systemd service and timer."
echo -e "${YELLOW}Configuration files (.env) will be preserved.${NC}"
echo ""
read -p "Continue with uninstall? (y/N) " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Uninstall cancelled."
    exit 0
fi

# Stop and disable timer
if sudo systemctl is-active --quiet solarstorm-scout.timer; then
    echo "Stopping timer..."
    sudo systemctl stop solarstorm-scout.timer
    echo -e "${GREEN}✓${NC} Timer stopped"
fi

if sudo systemctl is-enabled --quiet solarstorm-scout.timer 2>/dev/null; then
    echo "Disabling timer..."
    sudo systemctl disable solarstorm-scout.timer
    echo -e "${GREEN}✓${NC} Timer disabled"
fi

# Remove service files
if [ -f "/etc/systemd/system/solarstorm-scout.service" ]; then
    sudo rm /etc/systemd/system/solarstorm-scout.service
    echo -e "${GREEN}✓${NC} Service file removed"
fi

if [ -f "/etc/systemd/system/solarstorm-scout.timer" ]; then
    sudo rm /etc/systemd/system/solarstorm-scout.timer
    echo -e "${GREEN}✓${NC} Timer file removed"
fi

# Reload systemd
sudo systemctl daemon-reload
echo -e "${GREEN}✓${NC} Systemd reloaded"

echo ""
echo -e "${GREEN}Uninstall complete!${NC}"
echo ""
echo "Preserved files:"
echo "  - Project directory (contains .env and code)"
echo "  - Logs directory"
echo "  - Virtual environment (if created)"
echo ""
echo "To completely remove SolarStorm Scout:"
echo "  rm -rf /path/to/solarstorm-scout"
echo ""
