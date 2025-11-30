import { createClient } from '@supabase/supabase-js'

const supabaseUrl = 'https://nbijvleadmlfffubdcqu.supabase.co'
const supabaseAnonKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5iaWp2bGVhZG1sZmZmdWJkY3F1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQ0NDEwMjQsImV4cCI6MjA4MDAxNzAyNH0.Y52QsaF8BsIPHpP5ZqIW7UvCHVKJPdj6LniZYAZkka8'

export const supabase = createClient(supabaseUrl, supabaseAnonKey)