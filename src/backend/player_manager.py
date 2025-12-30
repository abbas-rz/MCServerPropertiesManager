import json
import os
import uuid
import requests

class PlayerManager:
    def __init__(self, server_dir):
        self.server_dir = server_dir
        self.whitelist_file = os.path.join(server_dir, "whitelist.json")
        self.banned_players_file = os.path.join(server_dir, "banned-players.json")

    def _load_json(self, filepath):
        if not os.path.exists(filepath):
            return []
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []

    def _save_json(self, filepath, data):
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)

    def get_whitelist(self):
        return self._load_json(self.whitelist_file)

    def add_to_whitelist(self, username):
        # Need to resolve UUID
        # For MVP, we might just add the name if UUID resolution fails or is skipped?
        # Minecraft requires UUIDs usually.
        player_uuid = self._get_uuid(username)
        if not player_uuid:
            return False, "Could not resolve UUID"

        whitelist = self.get_whitelist()
        # Check if already exists
        for entry in whitelist:
            if entry.get('name', '').lower() == username.lower():
                return False, "Player already whitelisted"

        whitelist.append({
            "uuid": player_uuid,
            "name": username
        })
        self._save_json(self.whitelist_file, whitelist)
        return True, "Player added"

    def remove_from_whitelist(self, username):
        whitelist = self.get_whitelist()
        new_whitelist = [p for p in whitelist if p.get('name', '').lower() != username.lower()]
        if len(whitelist) == len(new_whitelist):
            return False, "Player not found"
        
        self._save_json(self.whitelist_file, new_whitelist)
        return True, "Player removed"

    def get_banned_players(self):
        return self._load_json(self.banned_players_file)

    def ban_player(self, username, reason="Banned by operator"):
        player_uuid = self._get_uuid(username)
        if not player_uuid:
            return False, "Could not resolve UUID"

        bans = self.get_banned_players()
        for entry in bans:
            if entry.get('name', '').lower() == username.lower():
                return False, "Player already banned"

        bans.append({
            "uuid": player_uuid,
            "name": username,
            "created": "2024-01-01 00:00:00 +0000", # TODO: Real timestamp
            "source": "Console",
            "expires": "forever",
            "reason": reason
        })
        self._save_json(self.banned_players_file, bans)
        return True, "Player banned"

    def unban_player(self, username):
        bans = self.get_banned_players()
        new_bans = [p for p in bans if p.get('name', '').lower() != username.lower()]
        if len(bans) == len(new_bans):
            return False, "Player not found"
        
        self._save_json(self.banned_players_file, new_bans)
        return True, "Player unbanned"

    def _get_uuid(self, username):
        try:
            resp = requests.get(f"https://api.mojang.com/users/profiles/minecraft/{username}")
            if resp.status_code == 200:
                data = resp.json()
                # Insert hyphens into UUID
                raw_uuid = data['id']
                formatted_uuid = f"{raw_uuid[:8]}-{raw_uuid[8:12]}-{raw_uuid[12:16]}-{raw_uuid[16:20]}-{raw_uuid[20:]}"
                return formatted_uuid
        except Exception:
            pass
        return None
