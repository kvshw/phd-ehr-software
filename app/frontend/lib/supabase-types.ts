export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export type Database = {
  // Allows to automatically instantiate createClient with right options
  // instead of createClient<Database, { PostgrestVersion: 'XX' }>(URL, KEY)
  __InternalSupabase: {
    PostgrestVersion: "13.0.5"
  }
  public: {
    Tables: {
      adaptations: {
        Row: {
          id: string
          patient_id: string | null
          plan_json: Json
          timestamp: string | null
          user_id: string
        }
        Insert: {
          id?: string
          patient_id?: string | null
          plan_json: Json
          timestamp?: string | null
          user_id: string
        }
        Update: {
          id?: string
          patient_id?: string | null
          plan_json?: Json
          timestamp?: string | null
          user_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "adaptations_patient_id_fkey"
            columns: ["patient_id"]
            isOneToOne: false
            referencedRelation: "patients"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "adaptations_user_id_fkey"
            columns: ["user_id"]
            isOneToOne: false
            referencedRelation: "users"
            referencedColumns: ["id"]
          },
        ]
      }
      imaging: {
        Row: {
          created_at: string | null
          file_path: string
          id: string
          patient_id: string
          type: string
        }
        Insert: {
          created_at?: string | null
          file_path: string
          id?: string
          patient_id: string
          type: string
        }
        Update: {
          created_at?: string | null
          file_path?: string
          id?: string
          patient_id?: string
          type?: string
        }
        Relationships: [
          {
            foreignKeyName: "imaging_patient_id_fkey"
            columns: ["patient_id"]
            isOneToOne: false
            referencedRelation: "patients"
            referencedColumns: ["id"]
          },
        ]
      }
      labs: {
        Row: {
          created_at: string | null
          id: string
          lab_type: string
          normal_range: string | null
          patient_id: string
          timestamp: string
          value: number | null
        }
        Insert: {
          created_at?: string | null
          id?: string
          lab_type: string
          normal_range?: string | null
          patient_id: string
          timestamp?: string
          value?: number | null
        }
        Update: {
          created_at?: string | null
          id?: string
          lab_type?: string
          normal_range?: string | null
          patient_id?: string
          timestamp?: string
          value?: number | null
        }
        Relationships: [
          {
            foreignKeyName: "labs_patient_id_fkey"
            columns: ["patient_id"]
            isOneToOne: false
            referencedRelation: "patients"
            referencedColumns: ["id"]
          },
        ]
      }
      patients: {
        Row: {
          age: number
          created_at: string | null
          id: string
          name: string
          primary_diagnosis: string | null
          sex: string
          updated_at: string | null
        }
        Insert: {
          age: number
          created_at?: string | null
          id?: string
          name: string
          primary_diagnosis?: string | null
          sex: string
          updated_at?: string | null
        }
        Update: {
          age?: number
          created_at?: string | null
          id?: string
          name?: string
          primary_diagnosis?: string | null
          sex?: string
          updated_at?: string | null
        }
        Relationships: []
      }
      suggestions: {
        Row: {
          confidence: number | null
          created_at: string | null
          explanation: string
          id: string
          patient_id: string
          source: string
          text: string
          type: string
        }
        Insert: {
          confidence?: number | null
          created_at?: string | null
          explanation: string
          id?: string
          patient_id: string
          source: string
          text: string
          type: string
        }
        Update: {
          confidence?: number | null
          created_at?: string | null
          explanation?: string
          id?: string
          patient_id?: string
          source?: string
          text?: string
          type?: string
        }
        Relationships: [
          {
            foreignKeyName: "suggestions_patient_id_fkey"
            columns: ["patient_id"]
            isOneToOne: false
            referencedRelation: "patients"
            referencedColumns: ["id"]
          },
        ]
      }
      user_actions: {
        Row: {
          action_type: string
          id: string
          metadata: Json | null
          patient_id: string | null
          timestamp: string | null
          user_id: string
        }
        Insert: {
          action_type: string
          id?: string
          metadata?: Json | null
          patient_id?: string | null
          timestamp?: string | null
          user_id: string
        }
        Update: {
          action_type?: string
          id?: string
          metadata?: Json | null
          patient_id?: string | null
          timestamp?: string | null
          user_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "user_actions_patient_id_fkey"
            columns: ["patient_id"]
            isOneToOne: false
            referencedRelation: "patients"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "user_actions_user_id_fkey"
            columns: ["user_id"]
            isOneToOne: false
            referencedRelation: "users"
            referencedColumns: ["id"]
          },
        ]
      }
      users: {
        Row: {
          created_at: string | null
          email: string
          id: string
          password_hash: string
          role: string
          updated_at: string | null
        }
        Insert: {
          created_at?: string | null
          email: string
          id?: string
          password_hash: string
          role: string
          updated_at?: string | null
        }
        Update: {
          created_at?: string | null
          email?: string
          id?: string
          password_hash?: string
          role?: string
          updated_at?: string | null
        }
        Relationships: []
      }
      vitals: {
        Row: {
          bp_dia: number | null
          bp_sys: number | null
          created_at: string | null
          hr: number | null
          id: string
          pain: number | null
          patient_id: string
          rr: number | null
          spo2: number | null
          temp: number | null
          timestamp: string
        }
        Insert: {
          bp_dia?: number | null
          bp_sys?: number | null
          created_at?: string | null
          hr?: number | null
          id?: string
          pain?: number | null
          patient_id: string
          rr?: number | null
          spo2?: number | null
          temp?: number | null
          timestamp?: string
        }
        Update: {
          bp_dia?: number | null
          bp_sys?: number | null
          created_at?: string | null
          hr?: number | null
          id?: string
          pain?: number | null
          patient_id?: string
          rr?: number | null
          spo2?: number | null
          temp?: number | null
          timestamp?: string
        }
        Relationships: [
          {
            foreignKeyName: "vitals_patient_id_fkey"
            columns: ["patient_id"]
            isOneToOne: false
            referencedRelation: "patients"
            referencedColumns: ["id"]
          },
        ]
      }
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      [_ in never]: never
    }
    Enums: {
      [_ in never]: never
    }
    CompositeTypes: {
      [_ in never]: never
    }
  }
}

type DatabaseWithoutInternals = Omit<Database, "__InternalSupabase">

type DefaultSchema = DatabaseWithoutInternals[Extract<keyof Database, "public">]

export type Tables<
  DefaultSchemaTableNameOrOptions extends
    | keyof (DefaultSchema["Tables"] & DefaultSchema["Views"])
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
        DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
      DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])[TableName] extends {
      Row: infer R
    }
    ? R
    : never
  : DefaultSchemaTableNameOrOptions extends keyof (DefaultSchema["Tables"] &
        DefaultSchema["Views"])
    ? (DefaultSchema["Tables"] &
        DefaultSchema["Views"])[DefaultSchemaTableNameOrOptions] extends {
        Row: infer R
      }
      ? R
      : never
    : never

export type TablesInsert<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Insert: infer I
    }
    ? I
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Insert: infer I
      }
      ? I
      : never
    : never

export type TablesUpdate<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Update: infer U
    }
    ? U
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Update: infer U
      }
      ? U
      : never
    : never

export type Enums<
  DefaultSchemaEnumNameOrOptions extends
    | keyof DefaultSchema["Enums"]
    | { schema: keyof DatabaseWithoutInternals },
  EnumName extends DefaultSchemaEnumNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"]
    : never = never,
> = DefaultSchemaEnumNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"][EnumName]
  : DefaultSchemaEnumNameOrOptions extends keyof DefaultSchema["Enums"]
    ? DefaultSchema["Enums"][DefaultSchemaEnumNameOrOptions]
    : never

export type CompositeTypes<
  PublicCompositeTypeNameOrOptions extends
    | keyof DefaultSchema["CompositeTypes"]
    | { schema: keyof DatabaseWithoutInternals },
  CompositeTypeName extends PublicCompositeTypeNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"]
    : never = never,
> = PublicCompositeTypeNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"][CompositeTypeName]
  : PublicCompositeTypeNameOrOptions extends keyof DefaultSchema["CompositeTypes"]
    ? DefaultSchema["CompositeTypes"][PublicCompositeTypeNameOrOptions]
    : never

export const Constants = {
  public: {
    Enums: {},
  },
} as const

