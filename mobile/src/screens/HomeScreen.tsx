import React from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  ActivityIndicator,
  StyleSheet,
} from 'react-native';
import { useCapture } from '../hooks/useCapture';
import { DEFAULT_PORT } from '../modules/ScreenCapture';

const STATUS_LABELS: Record<string, string> = {
  idle: 'Ready',
  starting: 'Starting…',
  active: 'Sharing',
  stopping: 'Stopping…',
  error: 'Error',
};

const STATUS_COLORS: Record<string, string> = {
  idle: '#8E8E93',
  starting: '#FF9500',
  active: '#34C759',
  stopping: '#FF9500',
  error: '#FF3B30',
};

export default function HomeScreen() {
  const { status, errorMessage, start, stop } = useCapture();
  const [host, setHost] = React.useState('');
  const [port, setPort] = React.useState(String(DEFAULT_PORT));

  const isTransitioning = status === 'starting' || status === 'stopping';
  const isActive = status === 'active';

  function handlePress() {
    if (isActive) {
      stop();
    } else {
      const parsedPort = parseInt(port, 10) || DEFAULT_PORT;
      start(host.trim(), parsedPort);
    }
  }

  return (
    <View style={styles.container}>
      <Text style={styles.title}>ShareToMac</Text>
      <Text style={styles.subtitle}>Mirror your screen to your Mac over Wi-Fi</Text>

      <View style={styles.form}>
        <Text style={styles.label}>Mac IP Address</Text>
        <TextInput
          style={styles.input}
          placeholder="e.g. 192.168.1.42"
          placeholderTextColor="#8E8E93"
          value={host}
          onChangeText={setHost}
          keyboardType="numeric"
          autoCapitalize="none"
          editable={!isActive && !isTransitioning}
        />

        <Text style={styles.label}>UDP Port</Text>
        <TextInput
          style={styles.input}
          placeholder={String(DEFAULT_PORT)}
          placeholderTextColor="#8E8E93"
          value={port}
          onChangeText={setPort}
          keyboardType="numeric"
          editable={!isActive && !isTransitioning}
        />
      </View>

      <View style={styles.statusRow}>
        <View style={[styles.statusDot, { backgroundColor: STATUS_COLORS[status] }]} />
        <Text style={[styles.statusText, { color: STATUS_COLORS[status] }]}>
          {STATUS_LABELS[status]}
        </Text>
      </View>

      {errorMessage && (
        <Text style={styles.errorText}>{errorMessage}</Text>
      )}

      <TouchableOpacity
        style={[
          styles.button,
          isActive ? styles.buttonStop : styles.buttonStart,
          (isTransitioning || !host) && styles.buttonDisabled,
        ]}
        onPress={handlePress}
        disabled={isTransitioning || (!isActive && !host)}
      >
        {isTransitioning ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <Text style={styles.buttonText}>
            {isActive ? 'Stop Sharing' : 'Start Sharing'}
          </Text>
        )}
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1C1C1E',
    paddingHorizontal: 24,
    paddingTop: 80,
  },
  title: {
    fontSize: 32,
    fontWeight: '700',
    color: '#FFFFFF',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 15,
    color: '#8E8E93',
    marginBottom: 40,
  },
  form: {
    marginBottom: 32,
  },
  label: {
    fontSize: 13,
    fontWeight: '600',
    color: '#8E8E93',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
    marginBottom: 8,
  },
  input: {
    backgroundColor: '#2C2C2E',
    color: '#FFFFFF',
    borderRadius: 12,
    paddingHorizontal: 16,
    paddingVertical: 14,
    fontSize: 17,
    marginBottom: 20,
  },
  statusRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  statusDot: {
    width: 10,
    height: 10,
    borderRadius: 5,
    marginRight: 8,
  },
  statusText: {
    fontSize: 15,
    fontWeight: '600',
  },
  errorText: {
    fontSize: 13,
    color: '#FF3B30',
    marginBottom: 16,
  },
  button: {
    borderRadius: 14,
    paddingVertical: 18,
    alignItems: 'center',
    marginTop: 8,
  },
  buttonStart: {
    backgroundColor: '#0A84FF',
  },
  buttonStop: {
    backgroundColor: '#FF3B30',
  },
  buttonDisabled: {
    opacity: 0.4,
  },
  buttonText: {
    fontSize: 17,
    fontWeight: '600',
    color: '#FFFFFF',
  },
});
