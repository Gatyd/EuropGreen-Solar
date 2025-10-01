# Implémentation du Pré-remplissage des Formulaires d'Installation

## 📋 Vue d'ensemble

Ce document décrit l'implémentation du système de pré-remplissage automatique des informations dans les documents administratifs (CERFA, Mandat ENEDIS, CONSUEL).

## 🎯 Objectif

Éviter à l'utilisateur de retaper les mêmes informations dans chaque document administratif en pré-remplissant automatiquement les champs à partir des données déjà disponibles dans d'autres documents et sur la fiche d'installation.

## � Principe Important

**Chaque document a ses propres besoins et son niveau de détail**. Le pré-remplissage doit s'adapter intelligemment en fonction :
1. Du contenu de chaque document (certains sont plus détaillés que d'autres)
2. Des documents déjà remplis (ordre de priorité dynamique)
3. Du type d'information recherché (client vs installateur)

## 📊 Sources de Données Disponibles

### InstallationForm
```typescript
{
  client?: { first_name, last_name, phone_number, email } // PAS d'adresse
  offer: { first_name, last_name, email, phone, address }
  client_address: string // Adresse du client sur la fiche
  representation_mandate?: { ... } // Infos client + installateur
  cerfa16702?: { ... } // Infos très détaillées installateur + terrain
}
```

### Priorités par Type d'Information

#### Nom/Prénom Client
```
client > offer
```
→ Priorité à `form.client` car données plus fiables

#### Téléphone Client
```
client.phone_number > offer.phone
```

#### Adresse Client/Terrain
```
mandate.client_address > cerfa.land_street > form.client_address > offer.address
```
→ Pas d'adresse sur `form.client`

#### Informations Installateur
```
mandate > cerfa (si type company)
```

## 🔧 Documents Modifiés

### 1. ❌ Visite Technique - AUCUN PRÉ-REMPLISSAGE
**Raison** : Les signatures doivent être saisies manuellement à chaque fois.

### 2. ❌ Installation Effectuée - AUCUN PRÉ-REMPLISSAGE
**Raison** : Les signatures doivent être saisies manuellement à chaque fois.

### 3. ✅ CERFA 16702 (`administrative/Cerfa16702/Modal.vue`)

**Qui est le déclarant ?** → **L'installateur**, pas le client !

**Champs pré-remplis** :

| Champ | Source | Logique |
|-------|--------|---------|
| `declarant_type` | mandate | `'company'` si mandate existe, sinon `'individual'` |
| **Si `type='company'` (avec mandat)** |||
| `company_denomination` | mandate.company_name | Nom de l'entreprise |
| `company_siret` | mandate.company_siret | SIRET |
| `address_street` | mandate.company_head_office_address | Adresse siège social |
| `first_name` | mandate.represented_by | Nom du représentant |
| **Si `type='individual'` (sans mandat)** |||
| `first_name` | auth.user.first_name | Utilisateur connecté |
| `last_name` | auth.user.last_name | Utilisateur connecté |
| `email` | auth.user.email | Utilisateur connecté |
| `phone` | auth.user.phone_number | Utilisateur connecté |
| **Terrain (info client)** |||
| `land_street` | mandate.client_address > form.client_address > offer.address | Adresse du terrain |

**Code**:
```typescript
if (mandate) {
    draft.declarant_type = 'company'
    // Infos entreprise depuis mandat
} else if (user && user.is_staff) {
    draft.declarant_type = 'individual'
    // Infos utilisateur connecté
}
// Adresse terrain
draft.land_street = mandate.client_address || form.client_address || offer.address
```

### 4. ✅ Mandat ENEDIS (`administrative/EnedisMandate/Modal.vue`)

**Champs pré-remplis** :

#### Client
| Champ | Source | Priorité |
|-------|--------|----------|
| `client_name` | client > offer | `client.first_name + last_name` |
| `client_address` | mandate > cerfa > form.client_address > offer | Adresse complète |
| `client_civility` | mandate.client_civility | 'mr' ou 'mme' |

#### Installateur (Entreprise en charge)
| Champ | Source | Priorité |
|-------|--------|----------|
| `contractor_company_name` | mandate > cerfa | Nom société |
| `contractor_company_siret` | mandate > cerfa | SIRET |
| `contractor_company_represented_by_name` | mandate > — | Nom représentant |
| `contractor_company_represented_by_role` | mandate > — | Fonction |
| `contractor_address` | mandate > cerfa | Adresse |

**Code**:
```typescript
// Client - priorité: client > offer
draft.client_name = client ? 
  `${client.first_name} ${client.last_name}` : 
  `${offer.first_name} ${offer.last_name}`

// Adresse - priorité: mandate > cerfa > form > offer
draft.client_address = mandate.client_address || 
  cerfa.address_street || 
  form.client_address || 
  offer.address

// Installateur - priorité: mandate > cerfa (si type company)
if (mandate) {
  draft.contractor_company_name = mandate.company_name
  // ...
} else if (cerfa && cerfa.declarant_type === 'company') {
  draft.contractor_company_name = cerfa.company_denomination
  // ...
}
```

### 5. ✅ CONSUEL (`administrative/Consuel/Modal.vue`)

**Champs pré-remplis** :

#### Client
| Champ | Source | Priorité |
|-------|--------|----------|
| `client_name` | client > offer | `client.first_name + last_name` |
| `client_phone` | client > offer | Téléphone |
| `site_address_line1` | mandate > cerfa.land_street > form.client_address > offer | Adresse site |

#### Installateur
| Champ | Source | Priorité |
|-------|--------|----------|
| `installer_company_name` | mandate > cerfa | Nom société |
| `installer_address` | mandate > cerfa | Adresse |
| `installer_name` | mandate > — | Nom représentant |
| `installer_email` | cerfa.email | Email (si pas de mandat) |
| `installer_phone` | cerfa.phone | Téléphone (si pas de mandat) |

**Code**:
```typescript
// Client - priorité: client > offer
draft.client_name = client ? 
  `${client.first_name} ${client.last_name}` : 
  `${offer.first_name} ${offer.last_name}`

draft.client_phone = client?.phone_number || offer?.phone

// Adresse site - priorité: mandate > cerfa.land_street > form > offer
draft.site_address_line1 = mandate.client_address || 
  cerfa.land_street || 
  form.client_address || 
  offer.address

// Installateur - priorité: mandate > cerfa
if (mandate) {
  draft.installer_company_name = mandate.company_name
  draft.installer_address = mandate.company_head_office_address
  draft.installer_name = mandate.represented_by
} else if (cerfa && cerfa.declarant_type === 'company') {
  draft.installer_company_name = cerfa.company_denomination
  draft.installer_address = cerfa.address_street
  draft.installer_email = cerfa.email
  draft.installer_phone = cerfa.phone
}
```

## 💡 Logique Générale

### 1. Non-destructif
Le pré-remplissage ne s'applique **que si le champ est vide** :
```typescript
if (!draft.fieldName) {
  draft.fieldName = source
}
```

### 2. Condition : Document non existant
Le pré-remplissage ne s'active **que si le document n'existe pas déjà** :
```typescript
if (!f || props.documentExistant) return
```

### 3. Priorité Client > Offer
Pour les informations personnelles du client :
```typescript
if (client) {
  draft.client_name = `${client.first_name} ${client.last_name}`
} else if (offer) {
  draft.client_name = `${offer.first_name} ${offer.last_name}`
}
```

### 4. Cascade pour Adresses
```typescript
draft.address = 
  mandate?.client_address || 
  cerfa?.land_street || 
  form.client_address || 
  offer?.address || 
  ''
```

### 5. Fallback Intelligent pour Installateur
```typescript
if (mandate) {
  // Utiliser le mandat (source la plus fiable)
} else if (cerfa && cerfa.declarant_type === 'company') {
  // Fallback sur CERFA si entreprise
}
```

## ✅ Tests et Validation

### Vérifications
- ✅ **TypeScript** : Aucune erreur de compilation
- ✅ **Props** : form passé correctement aux modals
- ✅ **Watchers** : `immediate: true` pour exécution au montage
- ✅ **Priorités** : client > offer pour infos personnelles
- ✅ **Fallback** : mandate > cerfa pour installateur

### Cas de Test

| Document | Mandat | CERFA | Client | Résultat |
|----------|--------|-------|--------|----------|
| CERFA | ❌ | ❌ | ✅ | Type individual + user |
| CERFA | ✅ | ❌ | ✅ | Type company + mandate |
| ENEDIS | ✅ | ✅ | ✅ | Mandate prioritaire |
| ENEDIS | ❌ | ✅ | ✅ | CERFA + client |
| CONSUEL | ✅ | ✅ | ✅ | Mandate prioritaire |

## 🎓 Maintenabilité

### Ordre d'ajout des documents
1. **Mandat de représentation** → Infos installateur + quelques infos client
2. **CERFA 16702** → Infos détaillées installateur + terrain
3. **Mandat ENEDIS** → Utilise mandat + CERFA
4. **CONSUEL** → Utilise mandat + CERFA

### Ajout d'un nouveau document
1. Identifier les champs à pré-remplir
2. Déterminer les sources disponibles
3. Établir l'ordre de priorité selon le type d'info
4. Utiliser `if (!draft.field)` pour non-destruction
5. Ajouter `if (!f || props.documentExistant) return` en garde
6. Utiliser `{ immediate: true }` sur le watcher

---

**Date de création** : 30 septembre 2025  
**Dernière mise à jour** : 1 octobre 2025  
**Statut** : ✅ Implémentation corrigée et validée

