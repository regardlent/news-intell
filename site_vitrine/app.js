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

  // --- Démo : récupère les articles depuis l'API ---
  var API_URL = 'http://localhost:8000';
  var demo = document.getElementById('demo-resultats');
  if (demo) {
    fetch(API_URL + '/api/articles')
      .then(function (r) { return r.json(); })
      .then(function (articles) {
        demo.textContent = '';
        if (!articles.length) {
          demo.textContent = 'Aucune analyse. Lancez « news-intell executer ».';
          return;
        }
        articles.slice(0, 6).forEach(function (a) {
          var carte = document.createElement('article');
          var h = document.createElement('h3');
          h.textContent = a.titre || '';
          var p = document.createElement('p');
          p.textContent = a.resume_ia || a.resume || '';
          var pied = document.createElement('p');
          pied.className = 'pied-carte';
          pied.textContent = (a.source || '') + ' · ' + (a.thematique || 'Divers');
          carte.appendChild(h);
          carte.appendChild(p);
          carte.appendChild(pied);
          demo.appendChild(carte);
        });
      })
      .catch(function () {
        demo.textContent = 'API non joignable. Lancez « news-intell serveur » puis rechargez.';
      });
  }
});
