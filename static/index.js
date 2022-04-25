const validarRegistro = () => {
  const registerForm = document.getElementById("register_form");
  const password = document.getElementById("password");
  const password2 = document.getElementById("password2");
  if (password.value != password2.value) {
    swal({
      title: "¡ERROR!",
      text: "Las contraseñas no coinciden",
      icon: "error",
      closeOnClickOutside: false,
    });
  } else {
    registerForm.submit();
  }
};

const validarInputNumber = (event) =>
  event.target.value < 1 && (event.target.value = 1);
