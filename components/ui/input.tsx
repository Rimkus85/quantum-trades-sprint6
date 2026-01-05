import React, { forwardRef, useState } from "react";
import { TextInput, View, Text, Pressable, TextInputProps, StyleSheet } from "react-native";
import { cn } from "@/lib/utils";
import { useColors } from "@/hooks/use-colors";
import MaterialIcons from "@expo/vector-icons/MaterialIcons";

interface InputProps extends TextInputProps {
  label?: string;
  error?: string;
  leftIcon?: keyof typeof MaterialIcons.glyphMap;
  rightIcon?: keyof typeof MaterialIcons.glyphMap;
  onRightIconPress?: () => void;
  containerClassName?: string;
}

export const Input = forwardRef<TextInput, InputProps>(
  ({ label, error, leftIcon, rightIcon, onRightIconPress, containerClassName, className, ...props }, ref) => {
    const colors = useColors();
    const [isFocused, setIsFocused] = useState(false);

    return (
      <View className={cn("w-full", containerClassName)}>
        {label && (
          <Text className="text-muted text-sm mb-2 font-medium">{label}</Text>
        )}
        <View
          className={cn(
            "flex-row items-center bg-surface rounded-xl border px-4",
            isFocused ? "border-primary" : error ? "border-error" : "border-border"
          )}
        >
          {leftIcon && (
            <MaterialIcons
              name={leftIcon}
              size={20}
              color={error ? colors.error : isFocused ? colors.primary : colors.muted}
              style={styles.leftIcon}
            />
          )}
          <TextInput
            ref={ref}
            className={cn(
              "flex-1 py-4 text-foreground text-base",
              className
            )}
            placeholderTextColor={colors.muted}
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
            {...props}
          />
          {rightIcon && (
            <Pressable onPress={onRightIconPress} style={styles.rightIcon}>
              <MaterialIcons
                name={rightIcon}
                size={20}
                color={colors.muted}
              />
            </Pressable>
          )}
        </View>
        {error && (
          <Text className="text-error text-sm mt-1">{error}</Text>
        )}
      </View>
    );
  }
);

Input.displayName = "Input";

interface PasswordInputProps extends Omit<InputProps, "secureTextEntry" | "rightIcon" | "onRightIconPress"> {}

export const PasswordInput = forwardRef<TextInput, PasswordInputProps>(
  (props, ref) => {
    const [showPassword, setShowPassword] = useState(false);

    return (
      <Input
        ref={ref}
        secureTextEntry={!showPassword}
        rightIcon={showPassword ? "visibility-off" : "visibility"}
        onRightIconPress={() => setShowPassword(!showPassword)}
        {...props}
      />
    );
  }
);

PasswordInput.displayName = "PasswordInput";

// CPF Input with mask
interface CPFInputProps extends Omit<InputProps, "value" | "onChangeText"> {
  value: string;
  onChangeText: (value: string) => void;
}

export const CPFInput = forwardRef<TextInput, CPFInputProps>(
  ({ value, onChangeText, ...props }, ref) => {
    const formatCPF = (text: string) => {
      // Remove non-digits
      const digits = text.replace(/\D/g, "").slice(0, 11);
      
      // Apply mask
      let formatted = digits;
      if (digits.length > 3) {
        formatted = digits.slice(0, 3) + "." + digits.slice(3);
      }
      if (digits.length > 6) {
        formatted = formatted.slice(0, 7) + "." + formatted.slice(7);
      }
      if (digits.length > 9) {
        formatted = formatted.slice(0, 11) + "-" + formatted.slice(11);
      }
      
      return formatted;
    };

    const handleChange = (text: string) => {
      onChangeText(formatCPF(text));
    };

    return (
      <Input
        ref={ref}
        value={value}
        onChangeText={handleChange}
        keyboardType="numeric"
        maxLength={14}
        placeholder="000.000.000-00"
        {...props}
      />
    );
  }
);

CPFInput.displayName = "CPFInput";

const styles = StyleSheet.create({
  leftIcon: {
    marginRight: 12,
  },
  rightIcon: {
    padding: 4,
    marginLeft: 8,
  },
});
