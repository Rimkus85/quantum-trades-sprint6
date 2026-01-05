import React, { useState } from "react";
import { View, Text, Pressable, Modal, FlatList, StyleSheet } from "react-native";
import { cn } from "@/lib/utils";
import { useColors } from "@/hooks/use-colors";
import MaterialIcons from "@expo/vector-icons/MaterialIcons";
import { useSafeAreaInsets } from "react-native-safe-area-context";

interface SelectOption {
  label: string;
  value: string;
}

interface SelectProps {
  label?: string;
  placeholder?: string;
  value?: string;
  options: SelectOption[];
  onValueChange: (value: string) => void;
  error?: string;
  containerClassName?: string;
}

export function Select({
  label,
  placeholder = "Selecione...",
  value,
  options,
  onValueChange,
  error,
  containerClassName,
}: SelectProps) {
  const colors = useColors();
  const insets = useSafeAreaInsets();
  const [isOpen, setIsOpen] = useState(false);

  const selectedOption = options.find((opt) => opt.value === value);

  const handleSelect = (option: SelectOption) => {
    onValueChange(option.value);
    setIsOpen(false);
  };

  return (
    <View className={cn("w-full", containerClassName)}>
      {label && (
        <Text className="text-muted text-sm mb-2 font-medium">{label}</Text>
      )}
      <Pressable
        onPress={() => setIsOpen(true)}
        style={({ pressed }) => [
          styles.trigger,
          {
            backgroundColor: colors.surface,
            borderColor: error ? colors.error : colors.border,
          },
          pressed && styles.pressed,
        ]}
      >
        <Text
          style={[
            styles.triggerText,
            { color: selectedOption ? colors.foreground : colors.muted },
          ]}
        >
          {selectedOption?.label || placeholder}
        </Text>
        <MaterialIcons name="keyboard-arrow-down" size={24} color={colors.muted} />
      </Pressable>
      {error && <Text className="text-error text-sm mt-1">{error}</Text>}

      <Modal
        visible={isOpen}
        transparent
        animationType="fade"
        onRequestClose={() => setIsOpen(false)}
      >
        <Pressable
          style={styles.overlay}
          onPress={() => setIsOpen(false)}
        >
          <View
            style={[
              styles.modalContent,
              {
                backgroundColor: colors.surface,
                marginBottom: insets.bottom + 20,
              },
            ]}
          >
            <View style={[styles.modalHeader, { borderBottomColor: colors.border }]}>
              <Text style={[styles.modalTitle, { color: colors.foreground }]}>
                {label || "Selecione uma opção"}
              </Text>
              <Pressable onPress={() => setIsOpen(false)}>
                <MaterialIcons name="close" size={24} color={colors.muted} />
              </Pressable>
            </View>
            <FlatList
              data={options}
              keyExtractor={(item) => item.value}
              renderItem={({ item }) => (
                <Pressable
                  onPress={() => handleSelect(item)}
                  style={({ pressed }) => [
                    styles.option,
                    {
                      backgroundColor: item.value === value
                        ? colors.primary + "20"
                        : pressed
                        ? colors.border
                        : "transparent",
                    },
                  ]}
                >
                  <Text
                    style={[
                      styles.optionText,
                      {
                        color: item.value === value ? colors.primary : colors.foreground,
                        fontWeight: item.value === value ? "600" : "400",
                      },
                    ]}
                  >
                    {item.label}
                  </Text>
                  {item.value === value && (
                    <MaterialIcons name="check" size={20} color={colors.primary} />
                  )}
                </Pressable>
              )}
              style={styles.list}
            />
          </View>
        </Pressable>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  trigger: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    paddingVertical: 14,
    paddingHorizontal: 16,
    borderRadius: 12,
    borderWidth: 1,
  },
  pressed: {
    opacity: 0.8,
  },
  triggerText: {
    fontSize: 16,
    flex: 1,
  },
  overlay: {
    flex: 1,
    backgroundColor: "rgba(0, 0, 0, 0.5)",
    justifyContent: "flex-end",
  },
  modalContent: {
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    maxHeight: "60%",
  },
  modalHeader: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    padding: 16,
    borderBottomWidth: 1,
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: "600",
  },
  list: {
    paddingHorizontal: 8,
  },
  option: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    paddingVertical: 14,
    paddingHorizontal: 16,
    borderRadius: 8,
    marginVertical: 2,
  },
  optionText: {
    fontSize: 16,
  },
});
