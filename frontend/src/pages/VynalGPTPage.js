import React, { useState, useEffect, useRef } from 'react';
import './VynalGPTPage.css';
import Button from '../components/Button';
import Card from '../components/Card';
import Input from '../components/Input';
import { useAppContext } from '../context/AppContext';

// URL du serveur backend pour les appels à l'API Llama 3
const API_URL = 'http://localhost:5000';

// Pour déboguer
console.log("VynalGPTPage - API_URL:", API_URL);

// Composant pour les instructions d'installation de Llama3
const InstallLlama3Instructions = ({ onClose }) => {
  return (
    <Card className="install-instructions">
      <div className="install-header">
        <h3>Installation de Llama3</h3>
        <Button 
          className="btn-transparent"
          onClick={onClose}
        >
          <i className='bx bx-x'></i>
        </Button>
      </div>
      <div className="install-content">
        <p>Pour installer Llama3, exécutez l'une des commandes suivantes dans votre terminal :</p>
        <div className="code-block">
          <code>ollama pull llama3</code>
        </div>
        <p>Ou pour la version 8B plus légère :</p>
        <div className="code-block">
          <code>ollama pull llama3:8b</code>
        </div>
        <Button 
          type="primary"
          onClick={onClose}
        >
          <i className='bx bx-refresh'></i> Vérifier à nouveau la connexion
        </Button>
      </div>
    </Card>
  );
};

const VynalGPTPage = () => {
  const { documents, templates } = useAppContext();
  const [messages, setMessages] = useState([
    {
      id: 1,
      role: 'assistant',
      content: 'Bonjour ! Je suis Vynal GPT, votre assistant IA propulsé par Llama 3. Comment puis-je vous aider aujourd\'hui ?',
      timestamp: new Date()
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  const [showTemplates, setShowTemplates] = useState(false);
  const [showSuggestions, setShowSuggestions] = useState(true);
  const [showInstallInstructions, setShowInstallInstructions] = useState(false);
  const [modelInfo, setModelInfo] = useState({
    name: "Llama 3",
    version: "8B",
    status: "connecté"
  });
  const [serverStatus, setServerStatus] = useState({ isConnected: false, message: 'Non connecté...', ollamaFound: false, modelFound: false });
  const [installingModel, setInstallingModel] = useState(false);
  const [connectionMethod, setConnectionMethod] = useState('backend'); // 'backend' ou 'direct'
  
  const messagesEndRef = useRef(null);
  const chatContainerRef = useRef(null);

  // Fonction utilitaire pour tester la connexion directe à Ollama
  const testDirectConnection = async () => {
    try {
      console.log("Test direct de connexion à Ollama sur http://localhost:11434");
      const directResponse = await fetch("http://localhost:11434/api/tags", {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
        signal: AbortSignal.timeout(3000)
      });
      
      if (directResponse.ok) {
        const data = await directResponse.json();
        console.log("Connexion directe à Ollama réussie:", data);
        
        // Rechercher le modèle llama
        const llama3Model = data.models?.find(model => 
          model.name.toLowerCase().includes("llama3") || 
          model.name.toLowerCase().includes("llama-3") ||
          model.name.toLowerCase().includes("llama_3") ||
          model.name.toLowerCase().includes("llama")
        );
        
        if (llama3Model) {
          console.log("Modèle Llama trouvé en connexion directe:", llama3Model);
          setServerStatus({
            isConnected: true,
            message: `Connecté à Ollama (direct) - Modèle ${llama3Model.name} disponible`,
            ollamaFound: true,
            modelFound: true
          });
          setModelInfo({
            name: "Llama 3",
            version: llama3Model.name.includes(":") ? llama3Model.name.split(":")[1] : "8B",
            status: "connecté"
          });
          setConnectionMethod('direct');
          return true;
        }
      }
      return false;
    } catch (error) {
      console.log("Erreur lors du test direct à Ollama:", error);
      return false;
    }
  };

  // Suggestions prédéfinies
  const suggestions = [
    "Générer un document de présentation",
    "Résumer le contenu du dernier document",
    "Expliquer les termes juridiques de mon contrat",
    "Aide-moi à rédiger un email professionnel"
  ];

  // Vérifier la connexion au serveur au chargement
  useEffect(() => {
    checkServerConnection();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleInstallModel = async () => {
    try {
      setInstallingModel(true);
      setShowInstallInstructions(true);
      
      console.log("Lancement de l'installation de Llama3...");
      const response = await fetch(`${API_URL}/api/pull`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: "llama3",
          stream: false
        }),
      });
      
      if (!response.ok) {
        console.error("Erreur lors de l'installation:", response.status);
        const errorText = await response.text();
        console.error("Détails:", errorText);
        return;
      }
      
      console.log("Installation de Llama3 terminée avec succès");
      
      // Vérifier à nouveau la connexion après l'installation
      setTimeout(() => {
        checkServerConnection();
        setInstallingModel(false);
      }, 1000);
      
    } catch (error) {
      console.error("Erreur lors de l'installation:", error);
      setInstallingModel(false);
    }
  };

  const checkServerConnection = async () => {
    console.log("Tentative de connexion à Ollama sur", API_URL);
    try {
      // D'abord essayer via le backend
      const response = await fetch(`${API_URL}/api/models`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        },
        signal: AbortSignal.timeout(5000)
      }).catch((error) => {
        console.error("Erreur lors de la requête fetch au backend:", error);
        return null;
      });
      
      console.log("Réponse de la vérification de connexion via backend:", response);
      
      if (response && response.ok) {
        const data = await response.json();
        console.log("Modèles Ollama disponibles via backend:", data);
        console.log("Données brutes des modèles:", JSON.stringify(data));
        
        // Mise à jour préliminaire du statut
        setServerStatus(prev => ({
          ...prev,
          ollamaFound: true
        }));
        
        // Cas particulier: format de réponse différent entre API tags et models
        let modelsArray = [];
        
        if (data.models && Array.isArray(data.models)) {
          // Format standard
          modelsArray = data.models;
        } else if (Array.isArray(data)) {
          // Format alternatif possible
          modelsArray = data;
        }
        
        console.log("Tableau de modèles extrait:", modelsArray);
        
        // Vérifier si un modèle de type llama est disponible
        const llamaModels = modelsArray.filter(model => {
          const modelName = typeof model === 'string' 
            ? model.toLowerCase() 
            : (model.name ? model.name.toLowerCase() : '');
          
          return modelName.includes("llama");
        });
        
        console.log("Modèles Llama trouvés:", llamaModels);
        
        if (llamaModels.length > 0) {
          // Utiliser le premier modèle llama trouvé
          const llama3Model = llamaModels[0];
          const modelName = typeof llama3Model === 'string' ? llama3Model : llama3Model.name;
          
          console.log("Modèle Llama sélectionné:", modelName);
          
          setServerStatus({
            isConnected: true,
            message: `Connecté à Ollama - Modèle ${modelName} disponible`,
            ollamaFound: true,
            modelFound: true
          });
          
          setModelInfo({
            name: "Llama",
            version: modelName.includes(":") ? modelName.split(":")[1] : modelName.includes("3") ? "3" : "",
            status: "connecté"
          });
          
          setConnectionMethod('backend');
          return true;
        } else {
          console.warn("Ollama est disponible mais aucun modèle Llama n'a été trouvé");
          setServerStatus({
            isConnected: false,
            message: "Ollama disponible mais modèle Llama non trouvé",
            ollamaFound: true,
            modelFound: false
          });
          
          // Essayer l'installation automatique
          return false;
        }
      } else {
        // Essayer la connexion directe si le backend ne répond pas
        console.log("Le backend ne répond pas, tentative de connexion directe...");
        const directConnected = await testDirectConnection();
        
        if (!directConnected) {
          // Mode simulation locale si aucune connexion ne fonctionne
          console.log("Aucune connexion disponible, passage en mode simulation");
          setServerStatus({
            isConnected: false,
            message: "Mode simulation (Ollama non disponible)",
            ollamaFound: false,
            modelFound: false
          });
        }
      }
    } catch (error) {
      console.error("Erreur de connexion au serveur:", error);
      
      // Essayer la connexion directe en cas d'erreur
      console.log("Erreur avec le backend, tentative de connexion directe...");
      const directConnected = await testDirectConnection();
      
      if (!directConnected) {
        setServerStatus({
          isConnected: false,
          message: "Mode simulation (Ollama non disponible)",
          ollamaFound: false,
          modelFound: false
        });
      }
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleInputChange = (e) => {
    setInputMessage(e.target.value);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const callLlamaAPI = async (userQuery) => {
    console.log("Appel à l'API Ollama avec:", userQuery);
    try {
      // Appeler l'API d'Ollama avec exactement les mêmes paramètres que dans le backend Python
      const requestBody = {
        model: "llama3", // Si llama3 n'est pas trouvé, essayons "llama" qui existe peut-être
        prompt: userQuery,
        stream: false,
        options: {
          temperature: 0.1,
          top_p: 0.85,
          num_predict: 1024,
          frequency_penalty: 0.1,
          stop: ["\n\n\n", "###", "```"],
          timeout: 20,
          num_ctx: 2048,
          num_thread: 6,
          num_gpu: 1,
          repetition_penalty: 1.1
        }
      };

      console.log("Méthode de connexion:", connectionMethod);
      console.log("Requête à Ollama:", JSON.stringify(requestBody, null, 2));
      
      let apiUrl = `${API_URL}/api/generate`;
      
      // Si la connexion directe a été utilisée, appeler directement Ollama
      if (connectionMethod === 'direct') {
        apiUrl = "http://localhost:11434/api/generate";
      }
      
      console.log("Envoi de la requête à:", apiUrl);
      
      try {
        const response = await fetch(apiUrl, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(requestBody),
          signal: AbortSignal.timeout(60000) // 60 secondes de timeout comme dans le Python
        });

        console.log("Réponse d'Ollama:", response.status, response.statusText);

        if (response.ok) {
          const data = await response.json();
          console.log("Données reçues d'Ollama:", data);
          return data.response;
        } else {
          // Si l'erreur est une erreur de modèle non trouvé, essayons avec 'llama' au lieu de 'llama3'
          const errorText = await response.text();
          console.error("Erreur API Ollama:", errorText);
          
          if (errorText.includes("model not found") && requestBody.model === "llama3") {
            console.log("Modèle 'llama3' non trouvé, essai avec 'llama'");
            requestBody.model = "llama";
            
            const retryResponse = await fetch(apiUrl, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify(requestBody),
              signal: AbortSignal.timeout(60000)
            });
            
            if (retryResponse.ok) {
              const data = await retryResponse.json();
              console.log("Données reçues avec modèle 'llama':", data);
              return data.response;
            } else {
              throw new Error(`Erreur API Ollama avec 'llama': ${retryResponse.status} ${retryResponse.statusText}`);
            }
          } else {
            throw new Error(`Erreur API Ollama: ${response.status} ${response.statusText} - ${errorText}`);
          }
        }
      } catch (error) {
        throw error;
      }
    } catch (error) {
      console.error("Erreur d'appel à l'API Llama:", error);
      // En cas d'erreur, revenir au mode simulation
      return simulateLlama3Processing(userQuery);
    }
  };

  const simulateLlama3Processing = (query) => {
    // Cette fonction simule l'envoi à l'API Llama 3
    // Utilisée en mode fallback si le serveur n'est pas disponible
    return new Promise((resolve) => {
      // Simuler le délai de traitement du modèle
      const processingTime = Math.random() * 1000 + 1000; // Entre 1 et 2 secondes
      
      setTimeout(() => {
        resolve(processAIResponse(query));
      }, processingTime);
    });
  };

  const handleSendMessage = async () => {
    if (inputMessage.trim() === '' || isProcessing) return;

    // Ajouter le message de l'utilisateur
    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: inputMessage,
      timestamp: new Date()
    };

    setMessages(prevMessages => [...prevMessages, userMessage]);
    setInputMessage('');
    setIsProcessing(true);
    setShowSuggestions(false);

    // Signaler que Llama 3 est en train de traiter la demande
    setModelInfo(prev => ({...prev, status: "en traitement..."}));

    try {
      let response;
      
      // Si le serveur est connecté, utiliser l'API Ollama, sinon la simulation
      if (serverStatus.isConnected) {
        // Format du prompt exactement comme dans le backend Python
        const context = `Tu es un expert en rédaction de documents professionnels. 
        Génère un document basé sur la demande suivante : ${userMessage.content}
        Le document doit être en français, professionnel et bien structuré.`;
        
        response = await callLlamaAPI(context);
      } else {
        response = await simulateLlama3Processing(userMessage.content);
      }
      
      // Ajouter la réponse de l'IA
      const assistantMessage = {
        id: Date.now(),
        role: 'assistant',
        content: response,
        timestamp: new Date()
      };

      setMessages(prevMessages => [...prevMessages, assistantMessage]);
    } catch (error) {
      // Gérer les erreurs potentielles
      const errorMessage = {
        id: Date.now(),
        role: 'assistant',
        content: "Désolé, j'ai rencontré une erreur lors du traitement de votre demande. Veuillez vérifier que Ollama est en cours d'exécution et réessayer.",
        timestamp: new Date(),
        isError: true
      };
      
      setMessages(prevMessages => [...prevMessages, errorMessage]);
    } finally {
      setIsProcessing(false);
      setModelInfo(prev => ({...prev, status: "connecté"}));
    }
  };

  const processAIResponse = (userQuery) => {
    let response = '';
    
    // Analyser la requête de l'utilisateur et générer une réponse appropriée
    const query = userQuery.toLowerCase();
    
    if (query.includes('générer un document') || query.includes('créer un document')) {
      response = `Je peux vous aider à générer un document avec Llama 3. Veuillez me préciser le type de document que vous souhaitez créer (rapport, lettre, contrat, etc.) et son contenu principal.`;
    } 
    else if (query.includes('résumer') || query.includes('résumé')) {
      response = `Pour résumer un texte avec Llama 3, veuillez partager le contenu à résumer ou sélectionner un document existant dans votre bibliothèque.`;
    } 
    else if (query.includes('expliquer') || query.includes('contrat')) {
      response = `Je peux vous aider à comprendre les termes juridiques d'un contrat grâce à mes capacités d'analyse. Veuillez me partager le texte spécifique que vous souhaitez que j'explique.`;
    }
    else if (query.includes('template') || query.includes('modèle')) {
      response = `J'ai accès à ${templates.length} modèles. Vous pouvez cliquer sur le bouton "Voir les modèles" ci-dessous pour les consulter et en sélectionner un.`;
    }
    else if (query.includes('client') || query.includes('clients')) {
      response = `Je peux vous aider à retrouver des informations sur vos clients ou à préparer des documents personnalisés pour eux. Que souhaitez-vous faire exactement ?`;
    }
    else if (query.includes('llama') || query.includes('modèle')) {
      response = `Je suis propulsé par Llama 3, un modèle de langage avancé de Meta AI. J'utilise l'API Ollama pour communiquer avec le modèle. Actuellement, je fonctionne en ${serverStatus.isConnected ? 'mode connecté à Ollama' : 'mode simulation'}.`;
    }
    else if (query.includes('serveur') || query.includes('connexion') || query.includes('ollama')) {
      response = `État de connexion: ${serverStatus.message}. ${!serverStatus.isConnected ? "Actuellement, je fonctionne en mode simulation, mais je peux toujours vous aider avec vos documents et templates." : "Je suis connecté à Ollama et au modèle Llama 3 complet, prêt à vous assister."}`;
    }
    else {
      response = `Merci pour votre message. Je suis Vynal GPT, propulsé par Llama 3 via Ollama, et je peux vous aider à générer des documents, résumer des textes, ou expliquer des contrats. N'hésitez pas à me préciser comment je peux vous être utile.`;
    }

    return response;
  };

  const handleSuggestionClick = (suggestion) => {
    setInputMessage(suggestion);
  };

  const handleTemplateClick = (template) => {
    setSelectedTemplate(template);
    setShowTemplates(false);
    
    // Ajouter un message concernant le template sélectionné
    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: `Je souhaite utiliser le modèle "${template.title}"`,
      timestamp: new Date()
    };
    
    setMessages(prevMessages => [...prevMessages, userMessage]);
    
    // Simuler une réponse de l'IA concernant le template
    setIsProcessing(true);
    setModelInfo(prev => ({...prev, status: "en traitement..."}));
    
    setTimeout(() => {
      const assistantMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: `J'ai sélectionné le modèle "${template.title}". Quelles informations souhaitez-vous inclure dans ce document ?`,
        timestamp: new Date()
      };
      
      setMessages(prevMessages => [...prevMessages, assistantMessage]);
      setIsProcessing(false);
      setModelInfo(prev => ({...prev, status: "connecté"}));
    }, 1000);
  };

  const toggleTemplates = () => {
    setShowTemplates(!showTemplates);
  };

  return (
    <div className="vynalgpt-container">
      <div className="vynalgpt-header">
        <h1>VynalGPT</h1>
        <div className={`server-status ${serverStatus.isConnected ? 'connected' : serverStatus.ollamaFound ? 'warning' : 'error'}`}>
          <i className={serverStatus.isConnected ? "bx bx-plug" : "bx bx-error-circle"}></i>
          <span>{serverStatus.message}</span>
          {!serverStatus.isConnected && serverStatus.ollamaFound && !serverStatus.modelFound && (
            <Button 
              className="install-button"
              variant="primary"
              onClick={handleInstallModel}
              disabled={installingModel}
            >
              {installingModel ? (
                <>
                  <i className="bx bx-loader-alt bx-spin"></i> Installation...
                </>
              ) : (
                <>
                  <i className="bx bx-download"></i> Installer Llama3
                </>
              )}
            </Button>
          )}
        </div>
      </div>

      {showInstallInstructions && <InstallLlama3Instructions onClose={() => {
        setShowInstallInstructions(false);
        checkServerConnection();
      }} />}

      <div className="chat-container" ref={chatContainerRef}>
        <div className="chat-messages">
          {messages.map((message) => (
            <div 
              key={message.id} 
              className={`chat-message ${message.role === 'assistant' ? 'assistant-message' : 'user-message'} ${message.isError ? 'error-message' : ''}`}
            >
              <div className="message-avatar">
                <i className={`bx ${message.role === 'assistant' ? 'bx-bot' : 'bx-user'}`}></i>
              </div>
              <div className="message-content">
                <div className="message-text">{message.content}</div>
                <div className="message-time">
                  {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </div>
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        {showSuggestions && (
          <div className="suggestions-container">
            <div className="suggestions-title">Suggestions :</div>
            <div className="suggestions-list">
              {suggestions.map((suggestion, index) => (
                <div 
                  key={index} 
                  className="suggestion-item"
                  onClick={() => handleSuggestionClick(suggestion)}
                >
                  <i className='bx bx-bulb'></i>
                  <span>{suggestion}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {showTemplates && (
          <Card className="templates-container">
            <div className="templates-header">
              <h3>Sélectionner un modèle</h3>
              <Button variant="transparent" onClick={toggleTemplates}>
                <i className='bx bx-x'></i>
              </Button>
            </div>
            <div className="templates-list">
              {templates && templates.length > 0 ? (
                templates.map(template => (
                  <div 
                    key={template.id} 
                    className="template-item"
                    onClick={() => handleTemplateClick(template)}
                  >
                    <i className='bx bx-file'></i>
                    <span>{template.title}</span>
                  </div>
                ))
              ) : (
                <div className="empty-templates">
                  <i className='bx bx-info-circle'></i>
                  <span>Aucun modèle disponible</span>
                </div>
              )}
            </div>
          </Card>
        )}

        <div className="chat-input-container">
          <div className="chat-tools">
            <Button 
              variant="transparent" 
              className="tool-button"
              onClick={toggleTemplates}
            >
              <i className='bx bx-file'></i>
              <span>Modèles</span>
            </Button>
            <Button 
              variant="transparent" 
              className="tool-button"
            >
              <i className='bx bx-user'></i>
              <span>Clients</span>
            </Button>
            <Button 
              variant="transparent" 
              className="tool-button"
              onClick={checkServerConnection}
            >
              <i className='bx bx-refresh'></i>
              <span>Reconnecter</span>
            </Button>
          </div>
          <div className="input-wrapper chat-input">
            <textarea
              value={inputMessage}
              onChange={handleInputChange}
              onKeyPress={handleKeyPress}
              placeholder="Posez votre question à Vynal GPT..."
              disabled={isProcessing}
            />
            <Button 
              variant="primary" 
              className="send-button"
              onClick={handleSendMessage}
              disabled={inputMessage.trim() === '' || isProcessing}
            >
              {isProcessing ? (
                <i className='bx bx-loader-alt bx-spin'></i>
              ) : (
                <i className='bx bx-send'></i>
              )}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VynalGPTPage; 