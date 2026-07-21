// Field check quiz — instant feedback, per-quiz score, retry.
// Markup contract: .quiz > .q > .q-opts > button[data-correct] + .q-explain
document.querySelectorAll('.quiz').forEach(function (quiz) {
  var questions = Array.prototype.slice.call(quiz.querySelectorAll('.q'));
  var scoreEl = quiz.querySelector('.quiz-score .val');
  var answered = 0;
  var correct = 0;

  quiz.addEventListener('click', function (e) {
    var btn = e.target.closest('.q-opts button');
    if (btn) {
      var q = btn.closest('.q');
      if (q.classList.contains('answered')) return;
      q.classList.add('answered');
      answered++;
      var isRight = btn.hasAttribute('data-correct');
      if (isRight) correct++;
      btn.classList.add(isRight ? 'correct' : 'incorrect');
      q.querySelectorAll('.q-opts button').forEach(function (b) {
        if (b.hasAttribute('data-correct')) b.classList.add('correct');
        b.disabled = true;
      });
      if (answered === questions.length) {
        quiz.classList.add('done');
        if (scoreEl) scoreEl.textContent = correct + ' / ' + questions.length;
      }
      return;
    }
    if (e.target.closest('.quiz-retry')) {
      answered = 0;
      correct = 0;
      quiz.classList.remove('done');
      questions.forEach(function (q) {
        q.classList.remove('answered');
        q.querySelectorAll('.q-opts button').forEach(function (b) {
          b.classList.remove('correct', 'incorrect');
          b.disabled = false;
        });
      });
    }
  });
});
