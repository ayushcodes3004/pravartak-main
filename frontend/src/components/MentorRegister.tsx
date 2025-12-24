import React, { useState } from 'react';
import { Input } from './ui/input';
import { Button } from './ui/button';
import { Label } from './ui/label';
import { Alert, AlertDescription } from './ui/alert';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { GraduationCap } from 'lucide-react';
import { apiRegisterMentor } from '../lib/api';

interface MentorRegisterProps {
  onBackToLogin: () => void;
}

interface RegisterFormData {
  fullName: string;
  email: string;
  password: string;
  expertise: string;
}

const MentorRegister = ({ onBackToLogin }: MentorRegisterProps) => {
  const [formData, setFormData] = useState<RegisterFormData>({
    fullName: '',
    email: '',
    password: '',
    expertise: ''
  });
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { id, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [id]: value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const { fullName, email, password, expertise } = formData;
      
      // Basic validation
      if (!fullName || !email || !password || !expertise) {
        throw new Error('All fields are required');
      }

      if (password.length < 6) {
        throw new Error('Password must be at least 6 characters long');
      }

      if (!email.includes('@')) {
        throw new Error('Please enter a valid email address');
      }

      await apiRegisterMentor(formData);
      onBackToLogin();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Registration failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <Card className="w-full max-w-md shadow-lg border-0 bg-card/80 backdrop-blur-sm">
        <CardHeader className="text-center">
          <div className="flex justify-center mb-4">
            <div className="bg-primary/10 p-3 rounded-full">
              <GraduationCap className="h-8 w-8 text-primary" />
            </div>
          </div>
          <CardTitle>Mentor Registration</CardTitle>
          <CardDescription>
            Create your mentor account
          </CardDescription>
        </CardHeader>
        <CardContent>
        {error && (
          <Alert variant="destructive" className="mb-4">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="fullName">Full Name</Label>
            <Input
              id="fullName"
              placeholder="Enter your full name"
              value={formData.fullName}
              onChange={handleChange}
              disabled={isLoading}
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              type="email"
              placeholder="Enter your email"
              value={formData.email}
              onChange={handleChange}
              disabled={isLoading}
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="password">Password</Label>
            <Input
              id="password"
              type="password"
              placeholder="Create a password (min. 6 characters)"
              value={formData.password}
              onChange={handleChange}
              disabled={isLoading}
              required
              minLength={6}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="expertise">Expertise</Label>
            <Input
              id="expertise"
              placeholder="Enter your area of expertise"
              value={formData.expertise}
              onChange={handleChange}
              disabled={isLoading}
              required
            />
          </div>

          <Button 
            type="submit" 
            className="w-full mt-4"
            disabled={isLoading}
          >
            {isLoading ? 'Registering...' : 'Register as Mentor'}
          </Button>
        </form>

        <div className="text-center mt-4">
          <Button
            variant="link"
            className="text-primary hover:underline"
            onClick={onBackToLogin}
            disabled={isLoading}
          >
            Back to Login
          </Button>
        </div>
      </CardContent>
    </Card>
    </div>
  );
};

export default MentorRegister;