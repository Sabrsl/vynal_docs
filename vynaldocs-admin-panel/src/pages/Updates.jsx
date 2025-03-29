import React, { useState, useEffect } from 'react';
import { toast } from 'sonner';
import { settingsAPI } from '../utils/api';
import { Button } from '../components/ui/button';
import { Card } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { Download, RefreshCw, UploadCloud, Check, Clock, AlertTriangle } from 'lucide-react';
import { formatDate, formatBytes } from '../lib/utils';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogClose
} from '../components/ui/dialog';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "../components/ui/tooltip";
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "../components/ui/table";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../components/ui/select';
import {
  Tabs,
  TabsList,
  TabsTrigger,
  TabsContent,
} from "../components/ui/tabs";
import { Progress } from "../components/ui/progress";

function Updates() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [updateSettings, setUpdateSettings] = useState({
    autoCheckUpdates: true,
    updateChannel: 'stable',
    notifyOnUpdates: true,
    downloadAutomatically: false,
    installAutomatically: false
  });
  const [updateInfo, setUpdateInfo] = useState(null);
  const [updateHistory, setUpdateHistory] = useState([]);
  const [downloadProgress, setDownloadProgress] = useState(0);
  const [isDownloading, setIsDownloading] = useState(false);
  const [isInstalling, setIsInstalling] = useState(false);
  const [confirmUpdateOpen, setConfirmUpdateOpen] = useState(false);
  const [confirmUploadOpen, setConfirmUploadOpen] = useState(false);
  const [uploadedFile, setUploadedFile] = useState(null);
  const [actionInProgress, setActionInProgress] = useState(false);

  // Récupérer les paramètres de mise à jour et vérifier les mises à jour disponibles
  useEffect(() => {
    fetchUpdateSettings();
    checkForUpdates();
    fetchUpdateHistory();
  }, []);

  // Récupérer les paramètres de mise à jour
  const fetchUpdateSettings = async () => {
    try {
      setLoading(true);
      // Simulation d'une API
      const response = await settingsAPI.getUpdateSettings();
      setUpdateSettings(response.data || {
        autoCheckUpdates: true,
        updateChannel: 'stable',
        notifyOnUpdates: true,
        downloadAutomatically: false,
        installAutomatically: false
      });
    } catch (err) {
      setError('Impossible de charger les paramètres de mise à jour');
      console.error('Error fetching update settings:', err);
    } finally {
      setLoading(false);
    }
  };

  // Récupérer l'historique des mises à jour
  const fetchUpdateHistory = async () => {
    try {
      // Simulation d'une API
      const response = await settingsAPI.getUpdateHistory();
      setUpdateHistory(response.data || []);
    } catch (err) {
      console.error('Error fetching update history:', err);
    }
  };

  // Vérifier les mises à jour disponibles
  const checkForUpdates = async () => {
    try {
      setActionInProgress(true);
      // Simulation d'une API
      const response = await settingsAPI.checkForUpdates();
      setUpdateInfo(response.data || null);
      if (response.data) {
        toast.info(`Mise à jour ${response.data.version} disponible!`);
      } else {
        toast.success("Votre application est à jour!");
      }
    } catch (err) {
      setError('Impossible de vérifier les mises à jour');
      console.error('Error checking for updates:', err);
      toast.error("Erreur lors de la vérification des mises à jour");
    } finally {
      setActionInProgress(false);
    }
  };

  // Télécharger la mise à jour
  const downloadUpdate = async () => {
    try {
      setIsDownloading(true);
      setDownloadProgress(0);
      
      // Simulation de progrès
      const interval = setInterval(() => {
        setDownloadProgress(prev => {
          if (prev >= 95) {
            clearInterval(interval);
            return 95;
          }
          return prev + 5;
        });
      }, 500);
      
      // Simulation d'une API
      const response = await settingsAPI.downloadUpdate(updateInfo.id);
      
      clearInterval(interval);
      setDownloadProgress(100);
      
      if (response.success) {
        toast.success("Téléchargement terminé!");
        setUpdateInfo({
          ...updateInfo,
          downloaded: true,
          filePath: response.data.filePath
        });
      } else {
        toast.error("Erreur lors du téléchargement");
      }
    } catch (err) {
      setError('Impossible de télécharger la mise à jour');
      console.error('Error downloading update:', err);
      toast.error("Erreur lors du téléchargement");
    } finally {
      setIsDownloading(false);
    }
  };

  // Installer la mise à jour
  const installUpdate = async () => {
    try {
      setIsInstalling(true);
      
      // Simulation d'une API
      const response = await settingsAPI.installUpdate(updateInfo.filePath);
      
      if (response.success) {
        toast.success("Installation terminée! L'application va redémarrer.");
        setUpdateInfo(null);
        fetchUpdateHistory();
      } else {
        toast.error("Erreur lors de l'installation");
      }
    } catch (err) {
      setError('Impossible d\'installer la mise à jour');
      console.error('Error installing update:', err);
      toast.error("Erreur lors de l'installation");
    } finally {
      setIsInstalling(false);
      setConfirmUpdateOpen(false);
    }
  };

  // Installer une mise à jour depuis un fichier
  const installUploadedUpdate = async () => {
    try {
      setIsInstalling(true);
      
      // Simulation d'une API
      const formData = new FormData();
      formData.append('updateFile', uploadedFile);
      
      const response = await settingsAPI.installUploadedUpdate(formData);
      
      if (response.success) {
        toast.success("Installation terminée! L'application va redémarrer.");
        fetchUpdateHistory();
      } else {
        toast.error("Erreur lors de l'installation");
      }
    } catch (err) {
      setError('Impossible d\'installer la mise à jour');
      console.error('Error installing update:', err);
      toast.error("Erreur lors de l'installation");
    } finally {
      setIsInstalling(false);
      setConfirmUploadOpen(false);
      setUploadedFile(null);
    }
  };

  // Enregistrer les paramètres de mise à jour
  const saveUpdateSettings = async () => {
    try {
      setActionInProgress(true);
      
      // Simulation d'une API
      const response = await settingsAPI.updateUpdateSettings(updateSettings);
      
      if (response.success) {
        toast.success("Paramètres enregistrés");
      } else {
        toast.error("Erreur lors de l'enregistrement des paramètres");
      }
    } catch (err) {
      setError('Impossible d\'enregistrer les paramètres');
      console.error('Error saving update settings:', err);
      toast.error("Erreur lors de l'enregistrement des paramètres");
    } finally {
      setActionInProgress(false);
    }
  };

  // Gérer le changement d'un paramètre
  const handleSettingChange = (e) => {
    const { name, value, type, checked } = e.target;
    setUpdateSettings({
      ...updateSettings,
      [name]: type === 'checkbox' ? checked : value
    });
  };

  // Gérer le changement de canal de mise à jour
  const handleChannelChange = (value) => {
    setUpdateSettings({
      ...updateSettings,
      updateChannel: value
    });
  };

  // Gérer l'upload d'un fichier de mise à jour
  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      setUploadedFile(file);
      setConfirmUploadOpen(true);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Mises à jour</h2>
          <p className="text-muted-foreground">
            Gérez les mises à jour de l'application
          </p>
        </div>
        <div className="flex space-x-2">
          <Button 
            variant="outline" 
            onClick={checkForUpdates}
            disabled={actionInProgress}
          >
            <RefreshCw className={`mr-2 h-4 w-4 ${actionInProgress ? 'animate-spin' : ''}`} />
            Vérifier les mises à jour
          </Button>
          <div className="relative">
            <input
              type="file"
              id="update-file"
              accept=".zip,.update"
              onChange={handleFileUpload}
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            />
            <Button
              variant="outline"
              disabled={isInstalling}
            >
              <UploadCloud className="mr-2 h-4 w-4" />
              Installer depuis un fichier
            </Button>
          </div>
        </div>
      </div>

      {error && (
        <div className="bg-destructive/15 text-destructive text-sm p-4 rounded-md">
          {error}
        </div>
      )}

      <Tabs defaultValue="updates">
        <TabsList className="mb-6">
          <TabsTrigger value="updates">Mise à jour actuelle</TabsTrigger>
          <TabsTrigger value="history">Historique</TabsTrigger>
          <TabsTrigger value="settings">Paramètres</TabsTrigger>
        </TabsList>

        <TabsContent value="updates">
          <Card className="p-6">
            {loading ? (
              <div className="flex justify-center items-center h-40">
                <span className="inline-block animate-spin rounded-full h-8 w-8 border-2 border-current border-t-transparent"></span>
                <span className="ml-2">Vérification des mises à jour...</span>
              </div>
            ) : updateInfo ? (
              <div>
                <div className="flex items-center justify-between mb-6">
                  <div>
                    <h3 className="text-2xl font-semibold mb-2">Mise à jour {updateInfo.version} disponible</h3>
                    <p className="text-muted-foreground">
                      Publiée le {formatDate(updateInfo.releaseDate)}
                    </p>
                  </div>
                  <div className="flex items-center space-x-3">
                    {!updateInfo.downloaded ? (
                      <Button
                        onClick={downloadUpdate}
                        disabled={isDownloading}
                      >
                        {isDownloading ? (
                          <>
                            <span className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent"></span>
                            Téléchargement...
                          </>
                        ) : (
                          <>
                            <Download className="mr-2 h-4 w-4" />
                            Télécharger
                          </>
                        )}
                      </Button>
                    ) : (
                      <Button
                        onClick={() => setConfirmUpdateOpen(true)}
                        disabled={isInstalling}
                      >
                        {isInstalling ? (
                          <>
                            <span className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent"></span>
                            Installation...
                          </>
                        ) : (
                          <>
                            <UploadCloud className="mr-2 h-4 w-4" />
                            Installer
                          </>
                        )}
                      </Button>
                    )}
                  </div>
                </div>

                {isDownloading && (
                  <div className="mb-6">
                    <Progress value={downloadProgress} className="h-2 mb-2" />
                    <p className="text-sm text-right text-muted-foreground">
                      {downloadProgress}% terminé
                    </p>
                  </div>
                )}

                <div className="grid grid-cols-2 gap-6 mb-6">
                  <div className="space-y-2">
                    <p className="font-medium">Taille du fichier</p>
                    <p className="text-muted-foreground">{formatBytes(updateInfo.size)}</p>
                  </div>
                  <div className="space-y-2">
                    <p className="font-medium">Canal</p>
                    <p className="text-muted-foreground capitalize">{updateInfo.channel}</p>
                  </div>
                </div>

                <div className="space-y-2">
                  <p className="font-medium">Notes de version</p>
                  <div className="bg-muted p-4 rounded-md overflow-auto max-h-64">
                    <div className="prose prose-sm dark:prose-invert" dangerouslySetInnerHTML={{ __html: updateInfo.releaseNotes }} />
                  </div>
                </div>
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center h-40">
                <Check className="h-16 w-16 text-green-500 mb-4" />
                <h3 className="text-xl font-semibold mb-2">Votre application est à jour</h3>
                <p className="text-muted-foreground">
                  Version actuelle: {updateSettings?.currentVersion || '1.0.0'}
                </p>
              </div>
            )}
          </Card>
        </TabsContent>
        
        <TabsContent value="history">
          <Card>
            <div className="p-6">
              <h3 className="text-xl font-semibold mb-4">Historique des mises à jour</h3>
            </div>
            
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Version</TableHead>
                  <TableHead>Date d'installation</TableHead>
                  <TableHead>Canal</TableHead>
                  <TableHead>État</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {loading ? (
                  <TableRow>
                    <TableCell colSpan="4" className="text-center py-8">
                      <span className="inline-block animate-spin rounded-full h-4 w-4 border-2 border-current border-t-transparent mr-2"></span>
                      Chargement de l'historique...
                    </TableCell>
                  </TableRow>
                ) : updateHistory.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan="4" className="text-center py-8">
                      Aucune mise à jour trouvée
                    </TableCell>
                  </TableRow>
                ) : (
                  updateHistory.map((update, index) => (
                    <TableRow key={index}>
                      <TableCell className="font-medium">{update.version}</TableCell>
                      <TableCell>{formatDate(update.date)}</TableCell>
                      <TableCell className="capitalize">{update.channel}</TableCell>
                      <TableCell>
                        <div className="flex items-center">
                          {update.status === 'success' ? (
                            <span className="flex items-center text-green-500">
                              <Check className="h-4 w-4 mr-1" />
                              Succès
                            </span>
                          ) : update.status === 'failed' ? (
                            <span className="flex items-center text-red-500">
                              <AlertTriangle className="h-4 w-4 mr-1" />
                              Échec
                            </span>
                          ) : (
                            <span className="flex items-center text-yellow-500">
                              <Clock className="h-4 w-4 mr-1" />
                              Partiel
                            </span>
                          )}
                        </div>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </Card>
        </TabsContent>
        
        <TabsContent value="settings">
          <Card className="p-6">
            <h3 className="text-xl font-semibold mb-4">Paramètres de mise à jour</h3>
            
            <form className="space-y-6" onSubmit={(e) => { e.preventDefault(); saveUpdateSettings(); }}>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <label htmlFor="autoCheckUpdates" className="text-sm font-medium">
                    Vérifier automatiquement les mises à jour
                  </label>
                  <div>
                    <input
                      type="checkbox" 
                      id="autoCheckUpdates" 
                      name="autoCheckUpdates"
                      checked={updateSettings.autoCheckUpdates}
                      onChange={handleSettingChange}
                      className="h-4 w-4 rounded border-gray-300"
                    />
                  </div>
                </div>
                <p className="text-xs text-muted-foreground">
                  L'application vérifiera périodiquement les mises à jour disponibles
                </p>
              </div>
              
              <div className="space-y-2">
                <label htmlFor="updateChannel" className="text-sm font-medium">
                  Canal de mise à jour
                </label>
                <Select 
                  value={updateSettings.updateChannel} 
                  onValueChange={handleChannelChange}
                >
                  <SelectTrigger id="updateChannel">
                    <SelectValue placeholder="Sélectionner un canal" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="stable">Stable</SelectItem>
                    <SelectItem value="beta">Bêta</SelectItem>
                    <SelectItem value="dev">Développement</SelectItem>
                  </SelectContent>
                </Select>
                <p className="text-xs text-muted-foreground">
                  Stable: versions fiables testées, Beta: versions préliminaires pour test, Dev: versions expérimentales
                </p>
              </div>
              
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <label htmlFor="notifyOnUpdates" className="text-sm font-medium">
                    Notifier des mises à jour disponibles
                  </label>
                  <div>
                    <input
                      type="checkbox" 
                      id="notifyOnUpdates" 
                      name="notifyOnUpdates"
                      checked={updateSettings.notifyOnUpdates}
                      onChange={handleSettingChange}
                      className="h-4 w-4 rounded border-gray-300"
                    />
                  </div>
                </div>
                <p className="text-xs text-muted-foreground">
                  Affiche une notification lorsqu'une mise à jour est disponible
                </p>
              </div>
              
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <label htmlFor="downloadAutomatically" className="text-sm font-medium">
                    Télécharger automatiquement les mises à jour
                  </label>
                  <div>
                    <input
                      type="checkbox" 
                      id="downloadAutomatically" 
                      name="downloadAutomatically"
                      checked={updateSettings.downloadAutomatically}
                      onChange={handleSettingChange}
                      className="h-4 w-4 rounded border-gray-300"
                    />
                  </div>
                </div>
                <p className="text-xs text-muted-foreground">
                  Les mises à jour seront téléchargées automatiquement lorsqu'elles sont disponibles
                </p>
              </div>
              
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <label htmlFor="installAutomatically" className="text-sm font-medium">
                    Installer automatiquement les mises à jour
                  </label>
                  <div>
                    <input
                      type="checkbox" 
                      id="installAutomatically" 
                      name="installAutomatically"
                      checked={updateSettings.installAutomatically}
                      onChange={handleSettingChange}
                      className="h-4 w-4 rounded border-gray-300"
                    />
                  </div>
                </div>
                <p className="text-xs text-muted-foreground">
                  Les mises à jour seront installées automatiquement au redémarrage de l'application
                </p>
              </div>
              
              <div className="pt-4">
                <Button 
                  type="submit"
                  disabled={actionInProgress}
                >
                  {actionInProgress ? (
                    <>
                      <span className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent"></span>
                      Enregistrement...
                    </>
                  ) : (
                    'Enregistrer les paramètres'
                  )}
                </Button>
              </div>
            </form>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Modal de confirmation d'installation de mise à jour */}
      <Dialog open={confirmUpdateOpen} onOpenChange={setConfirmUpdateOpen}>
        <DialogContent className="sm:max-w-[450px]">
          <DialogHeader>
            <DialogTitle>Installer la mise à jour</DialogTitle>
            <DialogDescription>
              Voulez-vous installer la mise à jour {updateInfo?.version} ? L'application redémarrera après l'installation.
            </DialogDescription>
          </DialogHeader>
          
          <DialogFooter>
            <DialogClose asChild>
              <Button variant="outline" disabled={isInstalling}>Annuler</Button>
            </DialogClose>
            <Button 
              onClick={installUpdate} 
              disabled={isInstalling}
            >
              {isInstalling ? (
                <>
                  <span className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent"></span>
                  Installation...
                </>
              ) : (
                <>
                  <UploadCloud className="mr-2 h-4 w-4" />
                  Installer et redémarrer
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Modal de confirmation d'installation de fichier de mise à jour */}
      <Dialog open={confirmUploadOpen} onOpenChange={setConfirmUploadOpen}>
        <DialogContent className="sm:max-w-[450px]">
          <DialogHeader>
            <DialogTitle>Installer depuis un fichier</DialogTitle>
            <DialogDescription>
              Voulez-vous installer la mise à jour depuis le fichier {uploadedFile?.name} ? L'application redémarrera après l'installation.
            </DialogDescription>
          </DialogHeader>
          
          {uploadedFile && (
            <div className="py-4">
              <p className="mb-2">
                <span className="font-semibold">Fichier:</span> {uploadedFile.name}
              </p>
              <p className="mb-2">
                <span className="font-semibold">Taille:</span> {formatBytes(uploadedFile.size)}
              </p>
            </div>
          )}
          
          <DialogFooter>
            <DialogClose asChild>
              <Button 
                variant="outline" 
                disabled={isInstalling}
                onClick={() => setUploadedFile(null)}
              >
                Annuler
              </Button>
            </DialogClose>
            <Button 
              onClick={installUploadedUpdate} 
              disabled={isInstalling}
            >
              {isInstalling ? (
                <>
                  <span className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent"></span>
                  Installation...
                </>
              ) : (
                <>
                  <UploadCloud className="mr-2 h-4 w-4" />
                  Installer et redémarrer
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}

export default Updates; 