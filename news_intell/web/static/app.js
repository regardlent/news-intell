// Interactions de l'interface d'administration.
(function () {
  'use strict';

  function id(nom) { return document.getElementById(nom); }

  // --- Lancer une analyse ---
  var btn = id('btn-analyser');
  if (btn) {
    btn.addEventListener('click', function () {
      var statut = id('statut-tache');
      statut.textContent = 'Analyse lancée…';
      fetch('/admin/analyser', { method: 'POST' })
        .then(function (r) { return r.json(); })
        .then(function (d) {
          var idTache = d.id;
          var timer = setInterval(function () {
            fetch('/admin/taches/' + idTache)
              .then(function (r) { return r.json(); })
              .then(function (t) {
                statut.textContent = 'Statut : ' + t.statut + (t.resultat ? ' — ' + t.resultat : '');
                if (t.statut !== 'en_cours') { clearInterval(timer); }
              });
          }, 2000);
        });
    });
  }

  // --- Enregistrer la configuration ---
  var btnSave = id('btn-sauvegarder');
  if (btnSave) {
    btnSave.addEventListener('click', function () {
      var texte = id('config').value;
      var statut = id('statut-config');
      statut.textContent = 'Enregistrement…';
      fetch('/admin/config', { method: 'POST', body: texte })
        .then(function (r) { return r.json(); })
        .then(function (d) { statut.textContent = d.ok ? '✔ Configuration enregistrée.' : '✖ ' + d.erreur; });
    });
  }
  // --- Planifier une analyse ---
  var btnPlan = id('btn-planifier');
  if (btnPlan) {
    btnPlan.addEventListener('click', function () {
      var intervalle = id('intervalle').value;
      var statut = id('statut-planif');
      fetch('/admin/planifier?intervalle=' + intervalle, { method: 'POST' })
        .then(function (r) { return r.json(); })
        .then(function (d) {
          statut.textContent = d.ok ? '✔ Planification activée (toutes les ' + d.intervalle + ' min).' : '✖ ' + d.erreur;
        });
    });
  }
})();
