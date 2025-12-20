import { useState, useEffect } from 'react';
import { Heart, Loader2 } from 'lucide-react';
import { api } from '../App';

const FavoriteButton = ({ doctorId, size = 'md', onToggle }) => {
  const [isFavorite, setIsFavorite] = useState(false);
  const [favoriteId, setFavoriteId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    checkIfFavorite();
  }, [doctorId]);

  const checkIfFavorite = async () => {
    setChecking(true);
    try {
      const response = await api.get(`/favorites/doctors/check/${doctorId}`);
      setIsFavorite(response.data.is_favorite);
      setFavoriteId(response.data.favorite_id);
    } catch (error) {
      console.error('Error checking favorite:', error);
    } finally {
      setChecking(false);
    }
  };

  const toggleFavorite = async (e) => {
    e.stopPropagation(); // Prevent parent click events
    
    setLoading(true);
    try {
      if (isFavorite) {
        // Remove from favorites
        await api.delete(`/favorites/doctors/by-doctor/${doctorId}`);
        setIsFavorite(false);
        setFavoriteId(null);
      } else {
        // Add to favorites
        const response = await api.post('/favorites/doctors', {
          doctor_id: doctorId
        });
        setIsFavorite(true);
        setFavoriteId(response.data.favorite_id);
      }
      
      // Callback for parent component
      if (onToggle) {
        onToggle(!isFavorite);
      }
    } catch (error) {
      console.error('Error toggling favorite:', error);
      alert(error.response?.data?.detail || 'Error updating favorites');
    } finally {
      setLoading(false);
    }
  };

  const sizeClasses = {
    sm: 'w-6 h-6',
    md: 'w-8 h-8',
    lg: 'w-10 h-10'
  };

  const iconSizes = {
    sm: 'w-3 h-3',
    md: 'w-4 h-4',
    lg: 'w-5 h-5'
  };

  if (checking) {
    return (
      <button
        disabled
        className={`${sizeClasses[size]} rounded-full bg-gray-100 flex items-center justify-center`}
      >
        <Loader2 className={`${iconSizes[size]} text-gray-400 animate-spin`} />
      </button>
    );
  }

  return (
    <button
      onClick={toggleFavorite}
      disabled={loading}
      className={`${sizeClasses[size]} rounded-full flex items-center justify-center transition-all ${
        isFavorite
          ? 'bg-red-100 hover:bg-red-200'
          : 'bg-gray-100 hover:bg-gray-200'
      } disabled:opacity-50`}
      title={isFavorite ? 'Remove from favorites' : 'Add to favorites'}
    >
      {loading ? (
        <Loader2 className={`${iconSizes[size]} text-gray-600 animate-spin`} />
      ) : (
        <Heart
          className={`${iconSizes[size]} ${
            isFavorite ? 'text-red-500 fill-red-500' : 'text-gray-600'
          }`}
        />
      )}
    </button>
  );
};

export default FavoriteButton;
