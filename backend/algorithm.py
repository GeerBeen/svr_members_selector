from backend import dbfuncs

# app_profile - профіль заявки
# amount - кількість кандидатів
# key - тип кандидатів
# key=0 - кандидати з ідентичної спеціальності
# key=1 - кандидати з ідентичної або суміжною спеціальностей
# key=2 - кандидати з усіх можливих спеціальностей
def form_council(app_profile, amount, key=0):
    specialty = app_profile.specialty_id
    candidates = set()

    if key == 0:
        candidates.update( dbfuncs.get_cands_by_specialty(specialty) )
    elif key == 1:
        candidates.update( dbfuncs.get_cands_by_spec_range(specialty) )
    else:
        candidates.update( dbfuncs.get_all_cands() )

    app_profile.set_weights() # встановлюємо вагу ключових слів
    for cand in candidates:
        app_profile.compare(cand)

    sorted_cands = sorted(list(candidates), key=lambda c: c.suitability, reverse=True)
    return sorted_cands[:amount]