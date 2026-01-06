/**
 * Tela de Notificações
 */

import React, { useState } from "react";
import {
  ScrollView,
  Text,
  View,
  StyleSheet,
  TouchableOpacity,
  RefreshControl,
} from "react-native";
import { router } from "expo-router";
import { ScreenContainer } from "@/components/screen-container";
import { useColors } from "@/hooks/use-colors";
import MaterialIcons from "@expo/vector-icons/MaterialIcons";
import * as Haptics from "expo-haptics";
import { Platform } from "react-native";

// Notificações mockadas
const MOCK_NOTIFICATIONS = [
  {
    id: "1",
    type: "trade",
    title: "Operação Executada",
    message: "Compra de 100 PETR4 executada com sucesso",
    time: "Há 2 horas",
    read: false,
  },
  {
    id: "2",
    type: "alert",
    title: "Alerta de Preço",
    message: "VALE3 atingiu o preço alvo de R$ 70,00",
    time: "Há 5 horas",
    read: false,
  },
  {
    id: "3",
    type: "system",
    title: "Bem-vindo ao Quantum Trades!",
    message: "Seu período de trial de 7 dias começou. Aproveite todas as funcionalidades.",
    time: "Ontem",
    read: true,
  },
  {
    id: "4",
    type: "trade",
    title: "Operação Executada",
    message: "Venda de 50 VALE3 executada com sucesso",
    time: "Ontem",
    read: true,
  },
  {
    id: "5",
    type: "bot",
    title: "Bot Ativado",
    message: "Seu bot 'Cruzamento de Médias' foi ativado com sucesso",
    time: "2 dias atrás",
    read: true,
  },
];

export default function NotificationsScreen() {
  const colors = useColors();
  const [refreshing, setRefreshing] = useState(false);
  const [notifications, setNotifications] = useState(MOCK_NOTIFICATIONS);

  const handleRefresh = async () => {
    setRefreshing(true);
    await new Promise((resolve) => setTimeout(resolve, 1000));
    setRefreshing(false);
  };

  const handleBack = () => {
    if (Platform.OS !== "web") {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    }
    router.back();
  };

  const handleMarkAllRead = () => {
    if (Platform.OS !== "web") {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    }
    setNotifications(notifications.map((n) => ({ ...n, read: true })));
  };

  const handleNotificationPress = (id: string) => {
    if (Platform.OS !== "web") {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    }
    setNotifications(
      notifications.map((n) => (n.id === id ? { ...n, read: true } : n))
    );
  };

  const unreadCount = notifications.filter((n) => !n.read).length;

  return (
    <ScreenContainer className="p-0">
      <View style={styles.container}>
        {/* Header */}
        <View style={styles.header}>
          <TouchableOpacity onPress={handleBack} style={styles.backButton}>
            <MaterialIcons name="arrow-back" size={24} color={colors.foreground} />
          </TouchableOpacity>
          <Text style={[styles.headerTitle, { color: colors.foreground }]}>
            Notificações
          </Text>
          {unreadCount > 0 && (
            <TouchableOpacity onPress={handleMarkAllRead}>
              <Text style={[styles.markAllRead, { color: colors.primary }]}>
                Marcar todas
              </Text>
            </TouchableOpacity>
          )}
        </View>

        {/* Lista de Notificações */}
        <ScrollView
          style={styles.scrollView}
          contentContainerStyle={styles.scrollContent}
          showsVerticalScrollIndicator={false}
          refreshControl={
            <RefreshControl
              refreshing={refreshing}
              onRefresh={handleRefresh}
              tintColor={colors.primary}
            />
          }
        >
          {notifications.length === 0 ? (
            <View style={styles.emptyState}>
              <MaterialIcons name="notifications-none" size={64} color={colors.muted} />
              <Text style={[styles.emptyTitle, { color: colors.foreground }]}>
                Nenhuma notificação
              </Text>
              <Text style={[styles.emptySubtitle, { color: colors.muted }]}>
                Suas notificações aparecerão aqui
              </Text>
            </View>
          ) : (
            notifications.map((notification) => (
              <NotificationItem
                key={notification.id}
                notification={notification}
                onPress={() => handleNotificationPress(notification.id)}
              />
            ))
          )}
        </ScrollView>
      </View>
    </ScreenContainer>
  );
}

// Componente de Item de Notificação
function NotificationItem({
  notification,
  onPress,
}: {
  notification: typeof MOCK_NOTIFICATIONS[0];
  onPress: () => void;
}) {
  const colors = useColors();

  const getIcon = () => {
    switch (notification.type) {
      case "trade":
        return "swap-horiz";
      case "alert":
        return "notifications-active";
      case "bot":
        return "smart-toy";
      case "system":
      default:
        return "info";
    }
  };

  const getIconColor = () => {
    switch (notification.type) {
      case "trade":
        return colors.success;
      case "alert":
        return colors.warning;
      case "bot":
        return colors.primary;
      case "system":
      default:
        return colors.muted;
    }
  };

  return (
    <TouchableOpacity
      onPress={onPress}
      style={[
        styles.notificationItem,
        { backgroundColor: colors.surface },
        !notification.read && styles.unread,
      ]}
    >
      <View
        style={[
          styles.notificationIcon,
          { backgroundColor: getIconColor() + "20" },
        ]}
      >
        <MaterialIcons name={getIcon()} size={20} color={getIconColor()} />
      </View>
      <View style={styles.notificationContent}>
        <View style={styles.notificationHeader}>
          <Text style={[styles.notificationTitle, { color: colors.foreground }]}>
            {notification.title}
          </Text>
          {!notification.read && (
            <View style={[styles.unreadDot, { backgroundColor: colors.primary }]} />
          )}
        </View>
        <Text style={[styles.notificationMessage, { color: colors.muted }]}>
          {notification.message}
        </Text>
        <Text style={[styles.notificationTime, { color: colors.muted }]}>
          {notification.time}
        </Text>
      </View>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  header: {
    flexDirection: "row",
    alignItems: "center",
    paddingHorizontal: 20,
    paddingVertical: 16,
  },
  backButton: {
    marginRight: 16,
  },
  headerTitle: {
    flex: 1,
    fontSize: 20,
    fontWeight: "600",
  },
  markAllRead: {
    fontSize: 14,
    fontWeight: "500",
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    paddingHorizontal: 20,
    paddingBottom: 100,
  },
  emptyState: {
    alignItems: "center",
    paddingVertical: 80,
  },
  emptyTitle: {
    fontSize: 18,
    fontWeight: "600",
    marginTop: 16,
  },
  emptySubtitle: {
    fontSize: 14,
    marginTop: 8,
  },
  notificationItem: {
    flexDirection: "row",
    padding: 16,
    borderRadius: 12,
    marginBottom: 8,
  },
  unread: {
    borderLeftWidth: 3,
    borderLeftColor: "#FFD700",
  },
  notificationIcon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    alignItems: "center",
    justifyContent: "center",
    marginRight: 12,
  },
  notificationContent: {
    flex: 1,
  },
  notificationHeader: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
  },
  notificationTitle: {
    fontSize: 15,
    fontWeight: "600",
  },
  unreadDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
  },
  notificationMessage: {
    fontSize: 13,
    marginTop: 4,
    lineHeight: 18,
  },
  notificationTime: {
    fontSize: 11,
    marginTop: 6,
  },
});
