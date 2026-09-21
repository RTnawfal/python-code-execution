import unittest

from engine.corrector import corriger

EXERCICE = {
    "bareme": 4,
    "tests": [
        {"appel": "moyenne([10, 12, 14])", "attendu": 12.0, "tolerance": 0.001},
        {"appel": "moyenne([])", "attendu": 0},
    ],
    "erreurs_frequentes": [
        {"symptome": "ZeroDivisionError", "message": "La liste vide n'est pas traitée."},
    ],
}

QCM = {
    "type": "qcm",
    "bareme": 2,
    "questions": [
        {"enonce": "Type de 7 / 2 ?", "propositions": ["int", "float"], "reponse": 1},
        {"enonce": "Structures mutables ?", "propositions": ["liste", "tuple", "dict"], "reponse": [0, 2]},
    ],
}


class TestCorrigerCode(unittest.TestCase):
    def test_solution_correcte(self):
        correction = corriger(EXERCICE, "def moyenne(n):\n    return sum(n) / len(n) if n else 0\n")
        self.assertTrue(correction.reussi)
        self.assertEqual(correction.note, 4)

    def test_note_partielle(self):
        correction = corriger(EXERCICE, "def moyenne(n):\n    return sum(n) / len(n)\n")
        self.assertFalse(correction.reussi)
        self.assertEqual(correction.note, 2)

    def test_message_cible_sur_erreur_connue(self):
        correction = corriger(EXERCICE, "def moyenne(n):\n    return sum(n) / len(n)\n")
        self.assertEqual(correction.message, "La liste vide n'est pas traitée.")

    def test_code_invalide(self):
        correction = corriger(EXERCICE, "def moyenne(n)\n    return 0\n")
        self.assertFalse(correction.reussi)
        self.assertEqual(correction.note, 0.0)
        self.assertIn("SyntaxError", correction.message)

    def test_tolerance_flottante(self):
        exercice = {"bareme": 1, "tests": [{"appel": "f()", "attendu": 0.1, "tolerance": 0.001}]}
        self.assertTrue(corriger(exercice, "def f():\n    return 0.1000001\n").reussi)
        self.assertFalse(corriger(exercice, "def f():\n    return 0.2\n").reussi)


class TestCorrigerQcm(unittest.TestCase):
    def test_toutes_bonnes_reponses(self):
        correction = corriger(QCM, [1, [0, 2]])
        self.assertTrue(correction.reussi)
        self.assertEqual(correction.note, 2)

    def test_reponse_multiple_incomplete(self):
        correction = corriger(QCM, [1, [0]])
        self.assertFalse(correction.reussi)
        self.assertEqual(correction.note, 1)

    def test_ordre_des_choix_sans_importance(self):
        self.assertTrue(corriger(QCM, [1, [2, 0]]).reussi)

    def test_reponses_manquantes(self):
        correction = corriger(QCM, [])
        self.assertFalse(correction.reussi)
        self.assertEqual(correction.note, 0)


if __name__ == "__main__":
    unittest.main()
