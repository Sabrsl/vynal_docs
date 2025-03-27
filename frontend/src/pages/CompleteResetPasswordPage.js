import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import Button from '../components/Button';
import Input from '../components/Input';
import Loader from '../components/Loader';
import { useAuth } from '../context/AuthContext';
import './LoginPage.css';

const CompleteResetPasswordPage = () => {
  const { token } = useParams();
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [errors, setErrors] = useState({});
  const [isTokenValid, setIsTokenValid] = useState(true);

  const { completePasswordReset, isLoading, error } = useAuth();
  const navigate = useNavigate();

  // Valider le token (dans une application réelle, on vérifierait auprès du serveur)
  useEffect(() => {
    // Vérification simple que le token existe
    if (!token) {
      setIsTokenValid(false);
    }
  }, [token]);

  const validateForm = () => {
    const newErrors = {};

    if (!password) {
      newErrors.password = 'Le mot de passe est requis';
    } else if (password.length < 6) {
      newErrors.password = 'Le mot de passe doit contenir au moins 6 caractères';
    }

    if (password !== confirmPassword) {
      newErrors.confirmPassword = 'Les mots de passe ne correspondent pas';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (validateForm()) {
      try {
        const success = await completePasswordReset(token, password);
        if (success) {
          setIsSubmitted(true);
        }
      } catch (err) {
        console.error('Password reset error:', err);
      }
    }
  };

  if (!isTokenValid) {
    return (
      <div className="auth-container">
        <div className="auth-content">
          <div className="auth-card">
            <div className="auth-header">
              <div className="auth-logo">
                <i className='bx bx-file'></i>
                <h2>Vynal Docs</h2>
              </div>
              <h1>Lien Invalide</h1>
            </div>
            <div className="auth-error">
              <i className='bx bx-error-circle'></i>
              <span>Ce lien de réinitialisation est invalide ou a expiré.</span>
            </div>
            <Link to="/reset-password" className="btn btn-primary" style={{ marginTop: '16px', display: 'block', textAlign: 'center' }}>
              Demander un nouveau lien
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="auth-container">
      <div className="auth-content">
        <div className="auth-card">
          <div className="auth-header">
            <div className="auth-logo">
              <i className='bx bx-file'></i>
              <h2>Vynal Docs</h2>
            </div>
            <h1>Nouveau mot de passe</h1>
            <p>Définissez votre nouveau mot de passe</p>
          </div>

          {error && (
            <div className="auth-error">
              <i className='bx bx-error-circle'></i>
              <span>{error}</span>
            </div>
          )}

          {isSubmitted ? (
            <div className="auth-success">
              <i className='bx bx-check-circle'></i>
              <h3>Mot de passe modifié !</h3>
              <p>
                Votre mot de passe a été réinitialisé avec succès. Vous pouvez maintenant vous connecter avec votre nouveau mot de passe.
              </p>
              <Button
                variant="primary"
                onClick={() => navigate('/login')}
                style={{ width: '100%', marginTop: '16px' }}
              >
                Se connecter
              </Button>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="auth-form">
              <div className="form-group">
                <label htmlFor="password">Nouveau mot de passe</label>
                <Input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  prefixIcon="bx-lock-alt"
                  error={errors.password}
                />
                {errors.password && <div className="error-message">{errors.password}</div>}
              </div>

              <div className="form-group">
                <label htmlFor="confirmPassword">Confirmer le mot de passe</label>
                <Input
                  id="confirmPassword"
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="••••••••"
                  prefixIcon="bx-lock-alt"
                  error={errors.confirmPassword}
                />
                {errors.confirmPassword && <div className="error-message">{errors.confirmPassword}</div>}
              </div>

              <Button
                type="submit"
                variant="primary"
                disabled={isLoading}
                style={{ width: '100%', marginTop: '16px' }}
              >
                {isLoading ? <Loader size="small" /> : 'Réinitialiser le mot de passe'}
              </Button>
            </form>
          )}

          <div className="auth-footer">
            <p>
              <Link to="/login" className="login-link">
                <i className='bx bx-arrow-back'></i> Retour à la connexion
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CompleteResetPasswordPage; 