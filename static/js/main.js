document.addEventListener('DOMContentLoaded', function () {
  const roleSelect = document.getElementById('roleSelect');
  const farmerFields = document.getElementById('farmerFields');
  const providerFields = document.getElementById('providerFields');
  const buyerFields = document.getElementById('buyerFields');
  const languageSelect = document.querySelector('[data-language-selector]');

  if (roleSelect) {
    const toggleSections = () => {
      const role = roleSelect.value;
      if (farmerFields) farmerFields.style.display = role === 'farmer' ? 'flex' : 'none';
      if (providerFields) providerFields.style.display = role === 'provider' ? 'flex' : 'none';
      if (buyerFields) buyerFields.style.display = role === 'buyer' ? 'flex' : 'none';
    };

    roleSelect.addEventListener('change', toggleSections);
    toggleSections();
  }

  if (languageSelect) {
    languageSelect.addEventListener('change', function () {
      const language = this.value;
      const next = encodeURIComponent(window.location.pathname + window.location.search);
      window.location.href = `/set-language/${language}?next=${next}`;
    });
  }
});
