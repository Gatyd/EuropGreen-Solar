export default function catchErrors(err: any, toast: any) {
    const defaultErrMsg = 'Erreur du serveur, réessayer plus tard';
    console.log(err);
    
    // Gestion des erreurs serveur (5xx)
    if (err.response) {
      const status = err.response.status;
      if (status >= 500) {
        console.log(err.response)
        toast.add({
          icon: "i-heroicons-exclamation-circle-20-solid",
          title: defaultErrMsg,
          color: "error",
        });
        return;
      }
    }
    
    const err_data = (err as any).data;
    
    // Si pas de données d'erreur, afficher le message par défaut
    if (!err_data) {
      toast.add({
        icon: "i-heroicons-exclamation-circle-20-solid",
        title: defaultErrMsg,
        color: "error",
      });
      return;
    }
    
    // Fonction utilitaire pour formater le nom du champ
    const formatFieldName = (key: string): string => {
      const fieldTranslations: { [key: string]: string } = {
        'current_password': 'Mot de passe actuel',
        'password1': 'Nouveau mot de passe',
        'password2': 'Confirmation du mot de passe',
        'email': 'Email',
        'first_name': 'Prénom',
        'last_name': 'Nom',
        'non_field_errors': 'Erreur',
        'detail': 'Détail'
      };
      return fieldTranslations[key] || key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    };
    
    // Fonction utilitaire pour extraire le message d'une valeur
    const extractMessage = (value: any): string => {
      if (typeof value === 'string') {
        return value;
      }
      if (Array.isArray(value)) {
        return value.join(', ');
      }
      if (typeof value === 'object' && value !== null) {
        return JSON.stringify(value);
      }
      return String(value);
    };
    
    // Si err_data est une chaîne de caractères
    if (typeof err_data === 'string') {
      toast.add({
        icon: "i-heroicons-exclamation-circle-20-solid",
        title: "Erreur",
        description: err_data,
        color: "error",
      });
      return;
    }
    
    // Si err_data est un objet
    if (typeof err_data === 'object' && err_data !== null) {
      console.log(err_data);
      
      // Cas spécial pour les erreurs non liées à un champ spécifique
      if (err_data.detail) {
        toast.add({
          icon: "i-heroicons-exclamation-circle-20-solid",
          title: "Erreur",
          description: extractMessage(err_data.detail),
          color: "error",
        });
        return;
      }
      
      // Parcourir tous les champs d'erreur
      const entries = Object.entries(err_data);
      if (entries.length === 0) {
        toast.add({
          icon: "i-heroicons-exclamation-circle-20-solid",
          title: defaultErrMsg,
          color: "error",
        });
        return;
      }
      
      entries.forEach(([key, value]) => {
        const fieldName = formatFieldName(key);
        const message = extractMessage(value);
        
        toast.add({
          icon: "i-heroicons-exclamation-circle-20-solid",
          title: fieldName,
          description: message,
          color: "error",
        });
      });
      return;
    }
    
    // Fallback pour tout autre type de données
    toast.add({
      icon: "i-heroicons-exclamation-circle-20-solid",
      title: defaultErrMsg,
      color: "error",
    });
  }
  