import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

// Animated Page Wrapper
export const AnimatedPage = ({ children, className = "" }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.3, ease: "easeOut" }}
      className={className}
    >
      {children}
    </motion.div>
  );
};

// Animated Button
export const AnimatedButton = ({ children, onClick, disabled, className = "", variant = "primary" }) => {
  const baseClasses = "font-semibold py-3 px-6 rounded-xl transition-all duration-200 transform focus:outline-none focus:ring-2 focus:ring-offset-2";
  const variants = {
    primary: "bg-black hover:bg-gray-800 text-white focus:ring-black",
    secondary: "bg-gray-100 hover:bg-gray-200 text-gray-800 focus:ring-gray-500",
    danger: "bg-red-500 hover:bg-red-600 text-white focus:ring-red-500"
  };

  return (
    <motion.button
      whileHover={{ scale: 1.02, y: -2 }}
      whileTap={{ scale: 0.98, y: 0 }}
      onClick={onClick}
      disabled={disabled}
      className={`${baseClasses} ${variants[variant]} ${disabled ? 'opacity-50 cursor-not-allowed' : ''} ${className}`}
    >
      <motion.div
        initial={false}
        animate={{ x: 0 }}
        className="relative overflow-hidden"
      >
        {children}
      </motion.div>
    </motion.button>
  );
};

// Animated Card
export const AnimatedCard = ({ children, className = "", onClick, hover = true }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={hover ? { y: -4, scale: 1.02 } : {}}
      transition={{ duration: 0.3, ease: "easeOut" }}
      onClick={onClick}
      className={`bg-white rounded-2xl shadow-lg border border-gray-200 ${onClick ? 'cursor-pointer' : ''} ${className}`}
    >
      {children}
    </motion.div>
  );
};

// Swipeable Card Component
export const SwipeableCard = ({ children, onSwipeLeft, onSwipeRight, className = "" }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [swipeDirection, setSwipeDirection] = useState(null);

  return (
    <motion.div
      drag="x"
      dragConstraints={{ left: 0, right: 0 }}
      dragElastic={0.2}
      onDragStart={() => setIsDragging(true)}
      onDragEnd={(event, info) => {
        setIsDragging(false);
        const threshold = 100;
        if (info.offset.x > threshold) {
          setSwipeDirection('right');
          onSwipeRight && onSwipeRight();
        } else if (info.offset.x < -threshold) {
          setSwipeDirection('left');
          onSwipeLeft && onSwipeLeft();
        }
      }}
      onDrag={(event, info) => {
        if (info.offset.x > 50) {
          setSwipeDirection('right');
        } else if (info.offset.x < -50) {
          setSwipeDirection('left');
        } else {
          setSwipeDirection(null);
        }
      }}
      animate={{
        rotate: isDragging ? (swipeDirection === 'right' ? 5 : swipeDirection === 'left' ? -5 : 0) : 0,
        scale: isDragging ? 1.05 : 1
      }}
      className={`relative cursor-grab active:cursor-grabbing ${className}`}
      style={{ touchAction: 'none' }}
    >
      {children}
      
      {/* Swipe indicators */}
      <AnimatePresence>
        {swipeDirection === 'right' && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0 }}
            className="absolute top-4 right-4 bg-green-500 text-white px-3 py-1 rounded-full text-sm font-bold"
          >
            LIKE
          </motion.div>
        )}
        {swipeDirection === 'left' && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0 }}
            className="absolute top-4 left-4 bg-red-500 text-white px-3 py-1 rounded-full text-sm font-bold"
          >
            PASS
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

// Animated Message Bubble
export const AnimatedMessage = ({ message, isOwn, timestamp }) => {
  return (
    <motion.div
      initial={{ opacity: 0, x: isOwn ? 20 : -20, scale: 0.9 }}
      animate={{ opacity: 1, x: 0, scale: 1 }}
      transition={{ duration: 0.3, ease: "easeOut" }}
      className={`flex ${isOwn ? 'justify-end' : 'justify-start'} mb-4`}
    >
      <div className={`message-bubble p-3 ${isOwn ? 'sent' : 'received'}`}>
        <p className="text-sm">{message}</p>
        {timestamp && (
          <p className={`text-xs mt-1 ${isOwn ? 'text-gray-300' : 'text-gray-500'}`}>
            {new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </p>
        )}
      </div>
    </motion.div>
  );
};

// Typing Indicator
export const TypingIndicator = () => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: 10 }}
      className="typing-indicator"
    >
      <div className="typing-dots">
        <motion.div
          animate={{ scale: [0.8, 1.2, 0.8] }}
          transition={{ duration: 1.4, repeat: Infinity, ease: "easeInOut" }}
        />
        <motion.div
          animate={{ scale: [0.8, 1.2, 0.8] }}
          transition={{ duration: 1.4, repeat: Infinity, ease: "easeInOut", delay: 0.16 }}
        />
        <motion.div
          animate={{ scale: [0.8, 1.2, 0.8] }}
          transition={{ duration: 1.4, repeat: Infinity, ease: "easeInOut", delay: 0.32 }}
        />
      </div>
      <span className="ml-2 text-xs text-gray-500">Someone is typing...</span>
    </motion.div>
  );
};

// Match Celebration Modal
export const MatchCelebration = ({ isVisible, onClose, user }) => {
  useEffect(() => {
    if (isVisible) {
      const timer = setTimeout(() => {
        onClose();
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [isVisible, onClose]);

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="match-celebration"
          onClick={onClose}
        >
          <motion.div
            initial={{ scale: 0, rotate: -180 }}
            animate={{ scale: 1, rotate: 0 }}
            transition={{ duration: 0.6, ease: "backOut" }}
            className="text-center"
          >
            <motion.h1
              className="match-text mb-4"
              animate={{ 
                scale: [1, 1.1, 1],
                rotate: [0, 2, -2, 0]
              }}
              transition={{ 
                duration: 2,
                repeat: Infinity,
                ease: "easeInOut"
              }}
            >
              🎉 IT'S A MATCH! 🎉
            </motion.h1>
            {user && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 }}
                className="text-white text-xl"
              >
                You and {user.display_name} liked each other!
              </motion.div>
            )}
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 1 }}
              className="text-white text-sm mt-4"
            >
              Tap anywhere to continue
            </motion.p>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

// Animated Badge
export const AnimatedBadge = ({ count, className = "" }) => {
  if (!count || count === 0) return null;

  return (
    <motion.span
      initial={{ scale: 0 }}
      animate={{ scale: 1 }}
      exit={{ scale: 0 }}
      whileHover={{ scale: 1.1 }}
      transition={{ type: "spring", stiffness: 500, damping: 30 }}
      className={`absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center ${className}`}
    >
      {count > 99 ? '99+' : count}
    </motion.span>
  );
};

// Loading Dots Component
export const LoadingDots = ({ size = "sm" }) => {
  const sizes = {
    sm: "w-2 h-2",
    md: "w-3 h-3",
    lg: "w-4 h-4"
  };

  return (
    <div className="flex items-center justify-center space-x-1">
      {[0, 1, 2].map((index) => (
        <motion.div
          key={index}
          className={`${sizes[size]} bg-gray-600 rounded-full`}
          animate={{
            scale: [0.8, 1.2, 0.8],
            opacity: [0.5, 1, 0.5]
          }}
          transition={{
            duration: 1.5,
            repeat: Infinity,
            ease: "easeInOut",
            delay: index * 0.16
          }}
        />
      ))}
    </div>
  );
};

// Shimmer Loading Component
export const ShimmerLoading = ({ width = "100%", height = "20px", className = "" }) => {
  return (
    <div
      className={`shimmer rounded ${className}`}
      style={{ width, height }}
    />
  );
};

// Animated Input Field
export const AnimatedInput = ({ label, error, ...props }) => {
  const [isFocused, setIsFocused] = useState(false);

  return (
    <div className="form-field">
      <motion.label
        animate={{
          scale: isFocused || props.value ? 0.85 : 1,
          y: isFocused || props.value ? -10 : 0,
          color: isFocused ? "#000" : "#666"
        }}
        className="block text-sm font-medium mb-2"
      >
        {label}
      </motion.label>
      <motion.input
        {...props}
        onFocus={() => setIsFocused(true)}
        onBlur={() => setIsFocused(false)}
        whileFocus={{ scale: 1.02, y: -2 }}
        className={`w-full border border-gray-300 rounded-xl px-4 py-3 text-black placeholder-gray-500 focus:ring-2 focus:ring-black focus:border-transparent transition-all duration-300 ${error ? 'border-red-500' : ''}`}
      />
      <AnimatePresence>
        {error && (
          <motion.p
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="text-red-500 text-sm mt-1"
          >
            {error}
          </motion.p>
        )}
      </AnimatePresence>
    </div>
  );
};

// Staggered List Animation
export const StaggeredList = ({ children, className = "" }) => {
  const container = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const item = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0 }
  };

  return (
    <motion.div
      variants={container}
      initial="hidden"
      animate="show"
      className={className}
    >
      {React.Children.map(children, (child, index) => (
        <motion.div key={index} variants={item}>
          {child}
        </motion.div>
      ))}
    </motion.div>
  );
};

// Toast Notification
export const ToastNotification = ({ message, type = "info", isVisible, onClose }) => {
  const types = {
    success: "bg-green-500",
    error: "bg-red-500",
    warning: "bg-yellow-500",
    info: "bg-blue-500"
  };

  useEffect(() => {
    if (isVisible) {
      const timer = setTimeout(() => {
        onClose();
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [isVisible, onClose]);

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          initial={{ opacity: 0, y: -100, scale: 0.9 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: -100, scale: 0.9 }}
          className={`fixed top-4 right-4 ${types[type]} text-white px-6 py-3 rounded-lg shadow-lg z-50 max-w-sm`}
        >
          <div className="flex items-center justify-between">
            <span>{message}</span>
            <button
              onClick={onClose}
              className="ml-4 text-white hover:text-gray-200"
            >
              ×
            </button>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

// Floating Action Button
export const FloatingActionButton = ({ children, onClick, className = "" }) => {
  return (
    <motion.button
      whileHover={{ scale: 1.1, y: -2 }}
      whileTap={{ scale: 0.9 }}
      onClick={onClick}
      className={`fab ${className}`}
    >
      {children}
    </motion.button>
  );
};

// Profile Picture with Hover Animation
export const AnimatedProfilePicture = ({ src, alt, size = "w-12 h-12", className = "", onClick }) => {
  return (
    <motion.div
      whileHover={{ scale: 1.05 }}
      onClick={onClick}
      className={`${size} rounded-full overflow-hidden profile-picture ${className} ${onClick ? 'cursor-pointer' : ''}`}
    >
      <motion.img
        whileHover={{ scale: 1.1 }}
        src={src}
        alt={alt}
        className="w-full h-full object-cover"
      />
    </motion.div>
  );
};
