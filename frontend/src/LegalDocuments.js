import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const LegalModal = ({ isOpen, onClose, title, children }) => {
  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
        onClick={onClose}
      >
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.9, opacity: 0 }}
          className="bg-white rounded-2xl p-6 max-w-4xl w-full max-h-[90vh] overflow-y-auto"
          onClick={(e) => e.stopPropagation()}
        >
          <div className="flex items-center justify-between mb-6 border-b border-gray-200 pb-4">
            <h2 className="text-2xl font-bold text-black">{title}</h2>
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700 text-2xl"
            >
              ×
            </button>
          </div>

          <div className="text-gray-800 leading-relaxed">
            {children}
          </div>

          <div className="mt-8 pt-4 border-t border-gray-200 text-center">
            <button
              onClick={onClose}
              className="px-6 py-2 bg-black text-white rounded-lg hover:bg-gray-800 transition-colors"
            >
              Close
            </button>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export const PrivacyPolicy = ({ isOpen, onClose }) => (
  <LegalModal isOpen={isOpen} onClose={onClose} title="Privacy Policy">
    <div className="space-y-6">
      <div className="text-sm text-gray-600 mb-4">
        Last updated: January 1, 2025
      </div>

      <section>
        <h3 className="text-lg font-semibold mb-3">1. Information We Collect</h3>
        <p className="mb-3">
          When you use Solm8, we collect information that you provide directly to us, including:
        </p>
        <ul className="list-disc ml-6 space-y-2">
          <li>Account information (email, display name, username)</li>
          <li>Profile information (trading experience, preferred tokens, trading style)</li>
          <li>Communication data (messages, matches, interactions)</li>
          <li>Usage data (app activity, preferences, settings)</li>
          <li>Device information (browser type, IP address, device identifiers)</li>
        </ul>
      </section>

      <section>
        <h3 className="text-lg font-semibold mb-3">2. How We Use Your Information</h3>
        <p className="mb-3">We use the information we collect to:</p>
        <ul className="list-disc ml-6 space-y-2">
          <li>Provide and maintain our matching and communication services</li>
          <li>Personalize your experience and improve our algorithms</li>
          <li>Send you important updates and communications</li>
          <li>Ensure platform safety and prevent fraud</li>
          <li>Analyze usage patterns to enhance our platform</li>
        </ul>
      </section>

      <section>
        <h3 className="text-lg font-semibold mb-3">3. Information Sharing</h3>
        <p className="mb-3">
          We do not sell your personal information. We may share your information in the following circumstances:
        </p>
        <ul className="list-disc ml-6 space-y-2">
          <li><strong>With other users:</strong> Profile information visible to potential matches</li>
          <li><strong>With service providers:</strong> Third parties who help us operate our platform</li>
          <li><strong>For legal reasons:</strong> When required by law or to protect our rights</li>
          <li><strong>Business transfers:</strong> In connection with mergers or acquisitions</li>
        </ul>
      </section>

      <section>
        <h3 className="text-lg font-semibold mb-3">4. Data Security</h3>
        <p>
          We implement appropriate security measures to protect your personal information against unauthorized access, 
          alteration, disclosure, or destruction. However, no internet transmission is completely secure, and we cannot 
          guarantee absolute security.
        </p>
      </section>

      <section>
        <h3 className="text-lg font-semibold mb-3">5. Your Rights</h3>
        <p className="mb-3">You have the right to:</p>
        <ul className="list-disc ml-6 space-y-2">
          <li>Access, update, or delete your personal information</li>
          <li>Opt out of certain communications</li>
          <li>Request data portability</li>
          <li>Lodge complaints with regulatory authorities</li>
        </ul>
      </section>

      <section>
        <h3 className="text-lg font-semibold mb-3">6. Contact Us</h3>
        <p>
          If you have questions about this Privacy Policy, please contact us at{' '}
          <a href="mailto:support@solm8.app" className="text-blue-600 hover:underline">
            support@solm8.app
          </a>
        </p>
      </section>
    </div>
  </LegalModal>
);

export const TermsOfService = ({ isOpen, onClose }) => (
  <LegalModal isOpen={isOpen} onClose={onClose} title="Terms of Service">
    <div className="space-y-6">
      <div className="text-sm text-gray-600 mb-4">
        Last updated: January 1, 2025
      </div>

      <section>
        <h3 className="text-lg font-semibold mb-3">1. Acceptance of Terms</h3>
        <p>
          By accessing or using Solm8, you agree to be bound by these Terms of Service and our Privacy Policy. 
          If you do not agree to these terms, you may not use our service.
        </p>
      </section>

      <section>
        <h3 className="text-lg font-semibold mb-3">2. Description of Service</h3>
        <p className="mb-3">
          Solm8 is a social platform that connects Solana cryptocurrency traders. Our service includes:
        </p>
        <ul className="list-disc ml-6 space-y-2">
          <li>User matching based on trading preferences and experience</li>
          <li>Messaging and communication tools</li>
          <li>Profile creation and management</li>
          <li>Community features for traders</li>
        </ul>
      </section>

      <section>
        <h3 className="text-lg font-semibold mb-3">3. User Responsibilities</h3>
        <p className="mb-3">You agree to:</p>
        <ul className="list-disc ml-6 space-y-2">
          <li>Provide accurate and truthful information</li>
          <li>Maintain the confidentiality of your account</li>
          <li>Use the service in compliance with applicable laws</li>
          <li>Respect other users and avoid harassment</li>
          <li>Not use the platform for illegal activities</li>
          <li>Not share financial advice unless properly qualified</li>
        </ul>
      </section>

      <section>
        <h3 className="text-lg font-semibold mb-3">4. Trading Disclaimer</h3>
        <p className="font-medium text-red-600 mb-2">IMPORTANT RISK DISCLOSURE:</p>
        <p className="mb-3">
          Cryptocurrency trading involves substantial risk of loss and is not suitable for all investors. 
          Past performance is not indicative of future results. You should carefully consider whether 
          trading is appropriate for you in light of your financial condition.
        </p>
        <ul className="list-disc ml-6 space-y-2">
          <li>Solm8 does not provide financial or investment advice</li>
          <li>Users are solely responsible for their trading decisions</li>
          <li>We do not guarantee profits or prevent losses</li>
          <li>Always do your own research (DYOR)</li>
        </ul>
      </section>

      <section>
        <h3 className="text-lg font-semibold mb-3">5. Prohibited Conduct</h3>
        <p className="mb-3">You may not:</p>
        <ul className="list-disc ml-6 space-y-2">
          <li>Create fake profiles or impersonate others</li>
          <li>Engage in spam, scams, or fraudulent activities</li>
          <li>Share inappropriate or offensive content</li>
          <li>Attempt to manipulate our matching algorithms</li>
          <li>Violate intellectual property rights</li>
          <li>Use automated tools or bots</li>
        </ul>
      </section>

      <section>
        <h3 className="text-lg font-semibold mb-3">6. Account Termination</h3>
        <p>
          We reserve the right to suspend or terminate your account at any time for violations of these terms 
          or for any other reason at our sole discretion, with or without notice.
        </p>
      </section>

      <section>
        <h3 className="text-lg font-semibold mb-3">7. Limitation of Liability</h3>
        <p>
          Solm8 is provided "as is" without warranties. We are not liable for any damages arising from your 
          use of the platform, including but not limited to trading losses, missed opportunities, or data loss.
        </p>
      </section>

      <section>
        <h3 className="text-lg font-semibold mb-3">8. Changes to Terms</h3>
        <p>
          We may update these terms from time to time. We will notify users of significant changes via email 
          or platform notifications. Continued use of the service constitutes acceptance of updated terms.
        </p>
      </section>

      <section>
        <h3 className="text-lg font-semibold mb-3">9. Governing Law</h3>
        <p>
          These terms are governed by the laws of the jurisdiction where Solm8 is incorporated, without 
          regard to conflict of law principles.
        </p>
      </section>

      <section>
        <h3 className="text-lg font-semibold mb-3">10. Contact Information</h3>
        <p>
          For questions about these Terms of Service, please contact us at{' '}
          <a href="mailto:support@solm8.app" className="text-blue-600 hover:underline">
            support@solm8.app
          </a>
        </p>
      </section>
    </div>
  </LegalModal>
);