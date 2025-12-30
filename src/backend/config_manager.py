import os

class ConfigManager:
    def __init__(self, server_dir):
        self.config_path = os.path.join(server_dir, "server.properties")
        self.properties = {}

    def load_config(self):
        if not os.path.exists(self.config_path):
            return {}
        
        self.properties = {}
        with open(self.config_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        self.properties[key.strip()] = value.strip()
        return self.properties

    def save_config(self, new_properties):
        # Update internal properties with new values
        self.properties.update(new_properties)
        
        lines = []
        # Read existing file to preserve comments and order if possible, 
        # but for MVP we might just rewrite it or try to be smart.
        # Let's try to preserve comments and order.
        
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                existing_lines = f.readlines()
        else:
            existing_lines = []

        # Track which keys we've written
        written_keys = set()
        
        final_lines = []
        for line in existing_lines:
            stripped = line.strip()
            if stripped and not stripped.startswith('#') and '=' in stripped:
                key = stripped.split('=', 1)[0].strip()
                if key in self.properties:
                    final_lines.append(f"{key}={self.properties[key]}\n")
                    written_keys.add(key)
                else:
                    # Property removed or not in our list? Keep it if we didn't explicitly delete it.
                    # For this simple manager, we assume self.properties has the latest state of everything we care about.
                    # If it's not in self.properties, maybe we should keep it as is?
                    # But load_config loads everything. So if it's missing, it was deleted.
                    # However, the UI might only send back changed properties.
                    # Let's assume save_config receives the FULL dictionary of properties to save.
                    final_lines.append(line) # Keep original if not in new_properties? No, that's risky.
                    # Let's just rewrite the file for simplicity in MVP, but maybe keep the header.
                    pass
            else:
                final_lines.append(line)

        # Actually, a safer approach for MVP:
        # Just write everything out. We lose comments but it's safe.
        # Or, better: Read file, replace lines where keys match, append new keys.
        
        final_lines = []
        written_keys = set()
        
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                for line in f:
                    stripped = line.strip()
                    if stripped and not stripped.startswith('#') and '=' in stripped:
                        key = stripped.split('=', 1)[0].strip()
                        if key in self.properties:
                            final_lines.append(f"{key}={self.properties[key]}\n")
                            written_keys.add(key)
                        else:
                            # If it's not in the new properties, do we delete it?
                            # Usually yes. But let's assume the UI passes everything.
                            # If the UI passes a partial update, we need to merge.
                            # Let's assume self.properties is the source of truth.
                            if key in self.properties:
                                final_lines.append(f"{key}={self.properties[key]}\n")
                                written_keys.add(key)
                            else:
                                # If it was in the file but not in our properties map, 
                                # it might be a property we don't know about or one that was removed.
                                # Let's keep it to be safe, unless we want to strictly enforce the UI state.
                                final_lines.append(line)
                    else:
                        final_lines.append(line)
        
        # Append new keys that weren't in the file
        for key, value in self.properties.items():
            if key not in written_keys:
                final_lines.append(f"{key}={value}\n")

        with open(self.config_path, 'w') as f:
            f.writelines(final_lines)

    def get_property(self, key):
        return self.properties.get(key)

    def set_property(self, key, value):
        self.properties[key] = str(value)
