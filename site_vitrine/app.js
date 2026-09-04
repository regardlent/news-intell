// Interactions du site vitrine news-intell
document.addEventListener('DOMContentLoaded', function () {
  'use strict';

  var form = document.querySelector('.contact');
  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var conf = document.getElementById('confirmation');
      if (conf) { conf.textContent = 'Merci ! Nous reviendrons vers vous rapidement.'; }
    });
  }

  document.querySelectorAll('a[href^="#"]').forEach(function (lien) {
    lien.addEventListener('click', function (e) {
      var cible = document.querySelector(lien.getAttribute('href'));
      if (cible) { e.preventDefault(); cible.scrollIntoView({ behavior: 'smooth' }); }
    });
  });
});
