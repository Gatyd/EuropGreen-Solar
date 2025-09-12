import json
import os
import re
from typing import Any, Dict, List

from django.conf import settings
from rest_framework import serializers


def _slugify_label(label: str) -> str:
	"""Deprecated: conservé uniquement pour rétro-compat si le JSON contient encore 'label'."""
	s = label.lower().strip()
	s = re.sub(r"[^a-z0-9]+", "_", s)
	s = re.sub(r"_+", "_", s).strip("_")
	return s or "field"


class SC144AConfig:
	_cache: List[Dict[str, Any]] | None = None

	@classmethod
	def load(cls) -> List[Dict[str, Any]]:
		if cls._cache is not None:
			return cls._cache
		path = os.path.join(settings.BASE_DIR, "static", "json", "SC-144A.json")
		with open(path, "r", encoding="utf-8") as f:
			# prise en charge de commentaires '//' éventuels
			raw = f.read()
			raw = re.sub(r"//.*$", "", raw, flags=re.MULTILINE)
			data = json.loads(raw)
		# normalise: ensure page/w/h keys exist
		norm: List[Dict[str, Any]] = []
		for item in data:
			it = dict(item)
			it.setdefault("page", 1)
			# rétro-compat: si 'label' présent mais pas 'key', fabrique une clé
			if "key" not in it:
				it["key"] = _slugify_label(str(it.get("label", "field")))
			if it.get("type") == "image":
				# taille optionnelle, sinon gérée côté rendu
				it.setdefault("w", None)
				it.setdefault("h", None)
			norm.append(it)
		cls._cache = norm
		return norm


class SC144APreviewSerializer(serializers.Serializer):
	"""Serializer dynamique basé sur la configuration SC-144A.json.

	- Ajoute un champ par entrée (text -> CharField, checkbox -> BooleanField, image -> ImageField)
	- Les noms de champs sont slugifiés à partir du label.
	- Expose y_offset_mm pour ajuster le décalage vertical.
	- Conserve un mapping interne label->key pour l’étape de rendu.
	"""

	y_offset_mm = serializers.FloatField(required=False, default=8.0)

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._config = SC144AConfig.load()
		for item in self._config:
			key = str(item.get("key") or _slugify_label(str(item.get("label", ""))))
			t = item.get("type")
			if t == "text":
				self.fields[key] = serializers.CharField(required=False, allow_blank=True, default="")
			elif t == "checkbox":
				self.fields[key] = serializers.BooleanField(required=False, default=False)
			elif t == "image":
				# image facultative (aperçu)
				self.fields[key] = serializers.ImageField(required=False, allow_null=True)
			else:
				# fallback texte
				self.fields[key] = serializers.CharField(required=False, allow_blank=True, default="")

	def get_items(self) -> List[Dict[str, Any]]:
		"""Retourne la liste des items avec valeurs utilisateur (ou None)."""
		assert hasattr(self, "_config")
		out: List[Dict[str, Any]] = []
		vd: Dict[str, Any] = getattr(self, "validated_data", {})
		for item in self._config:
			key = str(item.get("key") or _slugify_label(str(item.get("label", ""))))
			value = vd.get(key, None)
			out.append({
				"label": item.get("label"),
				"key": key,
				"type": item.get("type"),
				"x": item.get("x"),
				"y": item.get("y"),
				"w": item.get("w"),
				"h": item.get("h"),
				"page": item.get("page", 1),
				"value": value,
			})
		return out

