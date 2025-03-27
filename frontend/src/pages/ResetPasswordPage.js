import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import Button from '../components/Button';
import Input from '../components/Input';
import Loader from '../components/Loader';
import { useAuth } from '../context/AuthContext';
import './LoginPage.css';

const ResetPasswordPage = () => {
  const [email, setEmail] = useState('');
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [errors, setErrors] = useState({});

  const { resetPassword, isLoading, error } = useAuth();
  const navigate = useNavigate();

  const validateForm = () => {
    const newErrors = {};

    if (!email.trim()) {
      newErrors.email = 'L\'email est requis';
    } else if (!/\S+@\S+\.\S+/.test(email)) {
      newErrors.email = 'L\'email est invalide';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (validateForm()) {
      try {
        const success = await resetPassword(email);
        if (success) {
          setIsSubmitted(true);
        }
      } catch (err) {
        console.error('Reset password error:', err);
      }
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-content">
        <div className="auth-card">
          <div className="auth-header">
            <div className="auth-logo">
              <i className='bx bx-file'></i>
              <h2>Vynal Docs</h2>
            </div>
            <h1>Réinitialisation du mot de passe</h1>
            <p>Entrez votre adresse e-mail pour réinitialiser votre mot de passe</p>
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
              <h3>E-mail envoyé !</h3>
              <p>
                Les instructions de réinitialisation de votre mot de passe ont été envoyées à {email}. 
                Veuillez vérifier votre boîte de réception.
              </p>
              <Button
                variant="primary"
                onClick={() => navigate('/login')}
                style={{ width: '100%', marginTop: '16px' }}
              >
                Retour à la connexion
              </Button>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="auth-form">
              <div className="form-group">
                <label htmlFor="email">Email</label>
                <Input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="votre@email.com"
                  prefixIcon="bx-envelope"
                  error={errors.email}
                />
                {errors.email && <div className="error-message">{errors.email}</div>}
                <small className="form-hint">
                  Saisissez l'adresse e-mail associée à votre compte. Vous recevrez un lien pour créer un nouveau mot de passe.
                </small>
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

export default ResetPasswordPage; 