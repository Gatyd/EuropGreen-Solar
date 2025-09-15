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


# Cache partagé des configs par template pour éviter les relectures disque
_TEMPLATE_CONFIG_CACHE: Dict[str, List[Dict[str, Any]]] = {}


def get_config_for_template(template: str) -> List[Dict[str, Any]]:
	"""Charge et met en cache la configuration JSON pour le template donné.

	Templates supportés: 144a, 144b, 144c, 144c2
	"""
	tpl = (template or "144a").strip().lower()
	if tpl not in {"144a", "144b", "144c", "144c2"}:
		tpl = "144a"
	if tpl in _TEMPLATE_CONFIG_CACHE:
		return _TEMPLATE_CONFIG_CACHE[tpl]

	file_name = {
		"144a": "SC-144A",
		"144b": "SC-144B",
		"144c": "SC-144C",
		"144c2": "SC-144C2",
	}[tpl]
	path = os.path.join(settings.BASE_DIR, "static", "json", f"{file_name}.json")
	with open(path, "r", encoding="utf-8") as f:
		raw = f.read()
		raw = re.sub(r"//.*$", "", raw, flags=re.MULTILINE)
		data = json.loads(raw)
	norm: List[Dict[str, Any]] = []
	for item in data:
		it = dict(item)
		it.setdefault("page", 1)
		if "key" not in it:
			it["key"] = _slugify_label(str(it.get("label", "field")))
		if it.get("type") == "image":
			it.setdefault("w", None)
			it.setdefault("h", None)
		norm.append(it)
	_TEMPLATE_CONFIG_CACHE[tpl] = norm
	return norm


class ConsuelPreviewSerializer(serializers.Serializer):
	"""Serializer dynamique basé sur la configuration du template Consuel (144a/b/c/c2).

	- Ajoute un champ par entrée (text -> CharField, checkbox -> BooleanField, image -> ImageField)
	- Les noms de champs sont basés sur 'key' du JSON (ou slugifiés à partir du label en fallback).
	- Expose y_offset_mm pour ajuster le décalage vertical.
	- Conserve la config en mémoire pour get_items().
	"""

	y_offset_mm = serializers.FloatField(required=False, default=8.0)

	def __init__(self, *args, **kwargs):
		# Permettre de passer template="144a|144b|144c|144c2"
		self._template = kwargs.pop("template", "144a")
		super().__init__(*args, **kwargs)
		self._config = get_config_for_template(self._template)
		for item in self._config:
			key = str(item.get("key") or _slugify_label(str(item.get("label", ""))))
			t = item.get("type")
			if t == "text":
				self.fields[key] = serializers.CharField(required=False, allow_blank=True, default="")
			elif t == "checkbox":
				self.fields[key] = serializers.BooleanField(required=False, default=False)
			elif t == "image":
				self.fields[key] = serializers.ImageField(required=False, allow_null=True)
			else:
				self.fields[key] = serializers.CharField(required=False, allow_blank=True, default="")

	def get_items(self) -> List[Dict[str, Any]]:
		"""Retourne la liste des items avec valeurs utilisateur (ou None)."""
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


# Sous-classes minces pour compatibilité/confort d'import
class SC144APreviewSerializer(ConsuelPreviewSerializer):
	def __init__(self, *args, **kwargs):
		kwargs.setdefault("template", "144a")
		super().__init__(*args, **kwargs)


class SC144BPreviewSerializer(ConsuelPreviewSerializer):
	def __init__(self, *args, **kwargs):
		kwargs.setdefault("template", "144b")
		super().__init__(*args, **kwargs)


class SC144CPreviewSerializer(ConsuelPreviewSerializer):
	def __init__(self, *args, **kwargs):
		kwargs.setdefault("template", "144c")
		super().__init__(*args, **kwargs)


class SC144C2PreviewSerializer(ConsuelPreviewSerializer):
	def __init__(self, *args, **kwargs):
		kwargs.setdefault("template", "144c2")
		super().__init__(*args, **kwargs)


