import React, { useState, useEffect, useRef } from 'react';
import { BrowserRouter as Router, Routes, Route, useParams, useNavigate } from 'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';
import {
  AnimatedPage,
  AnimatedButton,
  AnimatedCard,
  SwipeableCard,
  AnimatedMessage,
  TypingIndicator,
  MatchCelebration,
  AnimatedBadge,
  LoadingDots,
  ShimmerLoading,
  AnimatedInput,
  StaggeredList,
  ToastNotification,
  FloatingActionButton,
  AnimatedProfilePicture
} from './AnimatedComponents';
import { ReferralDashboard, SupportModal } from './ReferralComponents';
import PublicProfileModal from './PublicProfileModal';
import { PrivacyPolicy, TermsOfService } from './LegalDocuments';
