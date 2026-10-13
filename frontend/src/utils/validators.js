export const isValidEmail = (email) => {
  return /\S+@\S+\.\S+/.test(email);
};

export const isValidPassword = (password) => {
  return password && password.length >= 6;
};

