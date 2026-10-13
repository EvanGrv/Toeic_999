"""Original teaching material. No proprietary TOEIC questions are reproduced."""
import hashlib
import random

SKILLS = {
    'word-forms': 'Familles de mots', 'tenses': 'Temps et aspects',
    'connectors': 'Connecteurs logiques', 'prepositions': 'Prépositions',
    'agreement': 'Accords et structure', 'vocabulary': 'Vocabulaire professionnel',
    'detail': 'Repérage des détails', 'inference': 'Inférences',
    'intent': 'Intention et implicite', 'synthesis': 'Croisement de documents',
    'visual': 'Lecture de supports visuels',
}
PARTS = {1: 'Photographies', 2: 'Questions-réponses', 3: 'Conversations',
         4: 'Courts exposés', 5: 'Phrases incomplètes', 6: 'Textes à compléter', 7: 'Compréhension écrite'}
GROUPS = []

def q(stem, options, explanation, skill='detail', level='B2'):
    return {'stem': stem, 'choices': options.split('|'), 'answer': 0,
            'explanation': explanation, 'skill': skill, 'level': level}

def add(id, part, title, questions, **extra):
    group = {'id': id, 'part': part, 'title': title, 'questions': questions,
             'documents': [], 'transcript': '', 'source': 'Création originale · TOEIC 990+ AI',
             'status': 'published', **extra}
    for i, item in enumerate(questions):
        item['id'] = f'{id}-q{i + 1}'
        # Stable shuffling avoids a predictable answer position, including in exports.
        answer = item['choices'][item['answer']]
        random.Random(item['id']).shuffle(item['choices'])
        item['answer'] = item['choices'].index(answer)
    GROUPS.append(group)
    return group

GRAMMAR = [
('The revised safety guidelines must be followed ____ by all contractors.', 'strictly|strict|strictness|stricter', 'Strictly est un adverbe qui modifie followed. Strict et stricter sont des adjectifs ; strictness est un nom.', 'word-forms', 'B1'),
('The purchasing team has worked with this supplier ____ 2021.', 'since|for|during|within', 'Since introduit un point de départ. For attend une durée ; during une période-événement ; within exprime un délai maximal.', 'prepositions', 'B1'),
('Please submit the receipt ____ you can be reimbursed.', 'so that|despite|unless|whereas', 'So that introduit le but : pouvoir être remboursé. Despite exige un groupe nominal. Unless est une condition négative et whereas marque un contraste.', 'connectors', 'B2'),
('By the time the guests arrive tomorrow, the staff ____ the room.', 'will have prepared|had prepared|has prepared|preparing', 'Le futur antérieur situe la préparation avant un repère futur. Had prepared est passé ; has prepared présent ; preparing ne peut pas être le verbe conjugué seul.', 'tenses', 'B2'),
('Neither the manager nor the assistants ____ available this afternoon.', 'are|is|being|has', 'Avec neither…nor, on accorde ici avec le sujet le plus proche, assistants, pluriel : are. Is et has sont singuliers ; being ne forme pas seul le prédicat.', 'agreement', 'B2'),
('The board requested a ____ analysis of the proposed investment.', 'comprehensive|comprehensively|comprehend|comprehension', 'Le nom analysis est précédé d’un adjectif : comprehensive, complet. Comprehensively est un adverbe, comprehend un verbe et comprehension un nom.', 'word-forms', 'B2'),
('____ the heavy snowfall, all deliveries arrived on schedule.', 'Despite|Although|Because|Unless', 'Despite + groupe nominal exprime la concession. Although, because et unless doivent ici introduire une proposition avec un verbe.', 'connectors', 'B1'),
('The new software is compatible ____ our existing database.', 'with|to|for|at', 'La collocation est compatible with. To, for et at ne se construisent pas avec compatible dans ce sens.', 'prepositions', 'B1'),
('If the client had approved the design, we ____ production last week.', 'would have started|will start|would start|have started', 'Conditionnel irréel du passé : if + past perfect, would have + participe passé. Les autres temps ne situent pas le résultat contrefactuel dans le passé.', 'tenses', 'C1'),
('Employees are entitled ____ twenty days of annual leave.', 'to|for|with|at', 'Be entitled to signifie avoir droit à. For, with et at ne conviennent pas à cette construction.', 'prepositions', 'B2'),
('Each of the proposals ____ a detailed cost estimate.', 'includes|include|including|have included', 'Each est singulier, même suivi de of the proposals : includes. Include et have included ne s’accordent pas ; including n’est pas conjugué.', 'agreement', 'B1'),
('The consultant made several ____ recommendations.', 'practical|practically|practice|practiced', 'Practical qualifie recommendations et signifie utile/applicable. Practically est un adverbe ; practice un nom ; practiced qualifie une personne expérimentée.', 'word-forms', 'B1'),
('We will renew the lease ____ the landlord agrees to the repairs.', 'provided that|even though|in spite of|regardless of', 'Provided that pose la condition. Even though concède un fait ; in spite of et regardless of attendent un groupe nominal.', 'connectors', 'B2'),
('The shipment was delayed ____ a shortage of drivers.', 'because of|although|in order to|even if', 'Because of + groupe nominal donne la cause. Although et even if attendent une proposition ; in order to un verbe.', 'connectors', 'B1'),
('Ms. Patel is responsible for ____ the monthly inventory.', 'checking|check|checked|checks', 'Après la préposition for, le verbe prend la forme en -ing. Les trois formes conjuguées ou de base ne conviennent pas.', 'agreement', 'B1'),
('The merger is expected to ____ operating costs.', 'reduce|reduction|reduced|reducing', 'Expected to est suivi de la base verbale reduce. Reduction est un nom ; reduced et reducing ne peuvent pas suivre cet infinitif.', 'word-forms', 'B1'),
('Our customer service team responds to complaints ____.', 'promptly|prompt|promptness|prompted', 'Promptly modifie le verbe responds : rapidement. Prompt est adjectif, promptness un nom, prompted une forme verbale.', 'word-forms', 'B1'),
('The invoices ____ before the auditor arrived yesterday.', 'had been filed|will be filed|have been filing|are filing', 'Past perfect passif : les factures avaient été classées avant l’arrivée. Le futur est incohérent ; les formes actives donnent aux factures le rôle d’agent.', 'tenses', 'B2'),
('The training session is open to ____ wishes to improve their skills.', 'whoever|whomever|whose|which', 'Whoever est sujet de wishes. Whomever serait objet ; whose marque la possession ; which ne désigne pas librement toute personne.', 'agreement', 'C1'),
('The conference room is ____ enough to accommodate eighty people.', 'spacious|spaciously|space|spaces', 'Be + adjectif + enough : spacious enough. Spaciously est un adverbe, space et spaces des noms.', 'word-forms', 'B1'),
('Please make sure that all equipment is turned ____ before leaving.', 'off|over|into|up', 'Turn off = éteindre. Turn over = retourner, turn into = transformer, turn up = augmenter/apparaître.', 'vocabulary', 'B1'),
('No sooner had the presentation begun ____ the fire alarm rang.', 'than|when|then|that', 'La corrélation est no sooner…than. Hardly…when est une autre structure ; then et that ne complètent pas celle-ci.', 'connectors', 'C1'),
('The company offers a refund ____ thirty days of purchase.', 'within|among|beside|toward', 'Within borne un délai : dans les trente jours. Among indique un ensemble, beside une position, toward une direction.', 'prepositions', 'B1'),
('The revised contract contains ____ errors than the original.', 'fewer|less|little|much', 'Errors est dénombrable pluriel : fewer. Less/little/much s’emploient avec des noms indénombrables dans ce sens.', 'agreement', 'B2'),
('The product launch was postponed ____ the marketing team could complete its research.', 'so that|whether|despite|instead of', 'So that exprime le but du report. Whether introduit une alternative ; despite et instead of ne précèdent pas cette proposition.', 'connectors', 'B2'),
('The company has ____ its quarterly sales target.', 'exceeded|excess|excessive|excessively', 'Has + participe passé : exceeded, dépassé. Excess est un nom, excessive un adjectif, excessively un adverbe.', 'word-forms', 'B2'),
('All applicants must have at least three years of ____ experience.', 'relevant|relevance|relevantly|relate', 'Relevant experience signifie expérience pertinente. Le nom experience demande ici un adjectif, pas un nom, adverbe ou verbe.', 'word-forms', 'B1'),
('The office will remain closed ____ further notice.', 'until|by|during|since', 'Until further notice est l’expression jusqu’à nouvel ordre. By donne une échéance ; during une période ; since un départ dans le passé.', 'prepositions', 'B1'),
('If demand increases next month, we ____ additional staff.', 'will hire|would have hired|had hired|hiring', 'Condition réalisable future : if + présent, will + base verbale. Les autres formes expriment le passé ou sont incomplètes.', 'tenses', 'B1'),
('Not only ____ the deadline, but she also reduced the budget.', 'did she meet|she met|has she meeting|she meeting', 'Not only placé en tête déclenche l’inversion auxiliaire-sujet : did she meet. She met manque l’inversion ; les autres structures sont mal formées.', 'agreement', 'C1'),
('The technician recommended ____ the filter every six months.', 'replacing|replace|to replacing|replaced', 'Recommend + gérondif : replacing. La base verbale seule et to replacing ne conviennent pas ; replaced ne désigne pas l’action conseillée.', 'agreement', 'B2'),
('The two departments will work ____ to finish the project.', 'collaboratively|collaborative|collaboration|collaborate', 'Collaboratively est l’adverbe qui modifie work. Les autres formes sont adjectif, nom et verbe.', 'word-forms', 'B2'),
('The hotel provides a ____ shuttle service to the airport.', 'complimentary|complementary|compliment|complement', 'Complimentary signifie gratuit. Complementary signifie complémentaire. Compliment et complement ne sont pas les adjectifs attendus.', 'vocabulary', 'B2'),
('Please ____ the attached form and return it by Friday.', 'fill out|bring up|put off|take over', 'Fill out a form = remplir un formulaire. Bring up = évoquer ; put off = reporter ; take over = reprendre la responsabilité.', 'vocabulary', 'B1'),
('The committee insisted that the report ____ submitted today.', 'be|is|was|being', 'Après insist that au sens d’exigence, le subjonctif mandatif utilise la base be. Is/was sont indicatifs ; being est un participe.', 'agreement', 'C1'),
('The revised schedule is ____ to change without notice.', 'subject|object|matter|purpose', 'Subject to change = susceptible de modification. Object, matter et purpose ne forment pas cette expression.', 'vocabulary', 'B2'),
('Having ____ the inspection, the engineer signed the certificate.', 'completed|complete|completing|completion', 'Having + participe passé forme un participe parfait : having completed. Les autres formes ne complètent pas having.', 'tenses', 'B2'),
('The campaign was successful ____ its limited budget.', 'in spite of|because|although|even though', 'In spite of + groupe nominal exprime malgré. Because, although et even though attendent ici une proposition.', 'connectors', 'B1'),
('There is ____ evidence to support the claim.', 'insufficient|insufficiently|insufficiency|insufficiencies', 'Evidence demande l’adjectif insufficient. Insufficiently est adverbe ; insufficiency et insufficiencies sont des noms.', 'word-forms', 'B2'),
('The final decision depends ____ the results of the survey.', 'on|at|with|from', 'La construction est depend on. Les autres prépositions ne sont pas admises dans cette expression.', 'prepositions', 'B1'),
('The lease expires in June, ____ means we need to start looking now.', 'which|what|whose|who', 'Which reprend toute la proposition précédente. What ne s’utilise pas après un antécédent exprimé ; whose exprime la possession ; who une personne.', 'agreement', 'B2'),
('The director ____ the revised budget at yesterday’s meeting.', 'approved|has approved|will approve|approving', 'Yesterday’s meeting est un repère passé terminé : approved. Le present perfect ne se combine pas avec ce repère ; le futur et le participe sont incompatibles.', 'tenses', 'B1'),
('Our records show that your payment is still ____.', 'outstanding|outspoken|outgoing|outdated', 'Un paiement outstanding est en attente. Outspoken = franc ; outgoing = sociable/sortant ; outdated = obsolète.', 'vocabulary', 'B2'),
('The proposal is both financially viable ____ environmentally responsible.', 'and|but|or|nor', 'La paire est both…and. But, or et nor correspondent à d’autres coordinations.', 'connectors', 'B1'),
('____ you require assistance, please contact the reception desk.', 'Should|Would|Had|Were', 'Should + sujet + base verbale est une condition formelle équivalente à if you should require. Had attendrait required ; were une autre construction ; would ne convient pas.', 'agreement', 'C1'),
('The company is committed to ____ its environmental impact.', 'reducing|reduce|reduced|reduction of', 'Dans committed to, to est une préposition : reducing. Reduce n’est pas un gérondif ; reduced n’exprime pas l’action ; reduction of nécessiterait the.', 'agreement', 'B2'),
('The new policy will come into ____ on the first of next month.', 'effect|affect|effective|effectively', 'Come into effect = entrer en vigueur. Affect est principalement un verbe ; effective adjectif ; effectively adverbe.', 'vocabulary', 'B2'),
('This printer is considerably ____ than the model it replaced.', 'more efficient|most efficient|efficiency|efficiently', 'Than signale un comparatif : more efficient. Most est superlatif ; efficiency nom ; efficiently adverbe.', 'agreement', 'B1'),
('The contractor will be paid ____ completion of the work.', 'upon|onto|across|between', 'Upon completion signifie dès/à l’achèvement. Les autres prépositions indiquent ici des relations spatiales inadéquates.', 'prepositions', 'B2'),
('The report ____ on my desk since Monday.', 'has been|was being|had been|will have been', 'Since Monday jusqu’au présent appelle le present perfect. Had been demande un autre repère passé ; les autres temps ne traduisent pas cette continuité.', 'tenses', 'B1'),
('Seldom ____ such a detailed proposal from a new supplier.', 'have we received|we have received|we receiving|received we', 'Seldom en tête impose l’inversion have we received. Les autres constructions manquent l’auxiliaire ou l’ordre correct.', 'agreement', 'C1'),
('The supplier agreed to ____ the defective components at no charge.', 'replace|displace|misplace|place', 'Replace = remplacer les composants défectueux. Displace = déplacer/évincer ; misplace = égarer ; place = poser.', 'vocabulary', 'B1'),
('We need to ____ a decision before the end of the day.', 'make|do|perform|carry', 'La collocation est make a decision. Do, perform et carry ne s’emploient pas avec decision de cette manière.', 'vocabulary', 'B1'),
('The receptionist will notify you ____ the package arrives.', 'as soon as|as far as|in case of|despite', 'As soon as marque l’immédiateté temporelle. As far as exprime une portée ; in case of et despite attendent un nom.', 'connectors', 'B1'),
('The maintenance team worked overnight ____ disrupt normal operations.', 'so as not to|so as to not have|in spite of|in order that', 'So as not to + verbe exprime un but négatif. La seconde option rendrait la suite agrammaticale ; in spite of attend un nom ; in order that un sujet/verbe.', 'connectors', 'B2'),
('The warranty does not cover damage ____ by improper use.', 'caused|causing|causes|cause', 'Damage caused by réduit la relative passive damage that is caused by. Les formes actives changent le rôle de damage.', 'agreement', 'B2'),
('The auditor asked whether the figures had been ____ verified.', 'independently|independent|independence|depend', 'Independently modifie verified. Independent est adjectif, independence nom, depend verbe.', 'word-forms', 'B2'),
('The new regulations apply to all firms, ____ of their size.', 'regardless|regarding|regards|regarded', 'Regardless of = sans tenir compte de. Regarding est une préposition sans of ; regards et regarded ne forment pas cette locution.', 'vocabulary', 'B2'),
('Had the shipment arrived on time, the plant ____ to suspend operations.', 'would not have needed|will not need|does not need|has not needed', 'Had the shipment arrived équivaut à if…had arrived. Le résultat irréel passé se construit avec would not have needed.', 'tenses', 'C1'),
('The supplier’s assurance, plausible ____ it sounded, failed to convince the board.', 'though|despite|however|whereas', 'Adjectif + though + sujet/verbe exprime une concession inversée. Despite exige un nom ; however se place avant l’adjectif ; whereas ne permet pas cette inversion.', 'connectors', 'C2'),
('So substantial ____ the projected savings that the board approved the plan unanimously.', 'were|was|have|being', 'So + adjectif en tête déclenche l’inversion. Savings est pluriel : were. Was est singulier ; have et being ne forment pas la copule attendue.', 'agreement', 'C2'),
]
for i, (stem, opts, reason, skill, level) in enumerate(GRAMMAR):
    add(f'p5-{i+1:03}', 5, SKILLS[skill], [q(stem, opts, reason, skill, level)])

# Part 2: the question and all three choices are spoken, not printed in test mode.
RESPONSES = [
('Where can I find the updated price list?', 'It is on the shared drive.|The price has increased.|Yes, I listed them.', 'La question demande un lieu. Seule la référence au dossier partagé y répond.', 'detail'),
('Who is leading the workshop tomorrow?', 'I believe Ms. Chen is.|In the large meeting room.|It lasts two hours.', 'Who demande une personne, pas un lieu ou une durée.', 'detail'),
('Why was the delivery postponed?', 'The road was closed for repairs.|It is due on Friday.|I posted it yesterday.', 'Why demande une cause. La route fermée explique le report ; posted est un piège phonétique.', 'detail'),
('Would you prefer to meet on Tuesday or Wednesday?', 'Either day works for me.|The meeting was productive.|Yes, I prefer it.', 'Either day accepte les deux options. Une alternative n’appelle pas simplement yes.', 'intent'),
('Could you help me move these boxes?', 'Let me finish this email first.|They moved last month.|The boxes were inexpensive.', 'Réponse indirecte à une demande : la personne aidera après son courriel. Les autres réponses changent le sujet.', 'intent'),
('How long will the renovation take?', 'About three weeks.|On the second floor.|The room is quite long.', 'How long demande une durée, pas un emplacement ou une longueur physique.', 'detail'),
('Has the client approved the draft yet?', 'We are still waiting to hear back.|The draft is on the table.|Yes, the client is arriving.', 'Still waiting indique indirectement que l’approbation n’est pas encore reçue. Les distracteurs reprennent des mots sans répondre.', 'intent'),
('Where should I park the company van?', 'Behind the loading dock.|The park closes at six.|I bought it last year.', 'Park est ici le verbe garer. Behind the loading dock est le lieu demandé.', 'detail'),
('Is the printer still out of order?', 'The technician fixed it this morning.|I ordered paper yesterday.|It is the first one on the list.', 'Fixed it répond indirectement non. Order dans les distracteurs porte un autre sens.', 'intent'),
('When does your flight leave?', 'At a quarter past seven.|I am flying to Dublin.|The flight was comfortable.', 'When demande l’heure de départ, pas la destination ni une appréciation.', 'detail'),
('Shall we order lunch for the team?', 'That sounds like a good idea.|The team won yesterday.|It is in alphabetical order.', 'Shall we propose une action ; la bonne réponse accepte. Les distracteurs exploitent team et order.', 'intent'),
('How often are the safety checks carried out?', 'Every other month.|The check is on your desk.|By the main entrance.', 'How often demande une fréquence : tous les deux mois. Check au sens de chèque serait hors sujet.', 'detail'),
('Who should receive a copy of this report?', 'Send one to the regional director.|There are fifty copies.|The report is very thorough.', 'Who demande le destinataire. Le nombre de copies et la qualité du rapport ne répondent pas.', 'detail'),
('Do you know whether the café accepts card payments?', 'There is a cash machine next door, just in case.|The cards are on the shelf.|I paid attention in class.', 'Réponse pragmatique indirecte : un distributeur est proposé par précaution. Les autres emplois de card/paid sont hors contexte.', 'intent'),
('Why don’t we ask the supplier for a discount?', 'I have already tried that.|Because the supplier arrived.|The count was correct.', 'Why don’t we est une suggestion. La bonne réponse indique que cette démarche a déjà été tentée.', 'intent'),
('How much space will the new equipment require?', 'Roughly half of this room.|It costs six hundred dollars.|The space shuttle launched.', 'La question porte sur l’espace occupé. Le prix et le véhicule spatial ne conviennent pas.', 'detail'),
('Are you attending the trade fair next month?', 'Only if my travel budget is approved.|The fare is reasonable.|There are twelve months.', 'Une participation conditionnelle répond à la question. Fare ressemble à fair sans avoir le même sens.', 'intent'),
('Could you send me the revised schedule?', 'I will email it right away.|The train was delayed.|Yes, I revised for the exam.', 'La demande porte sur l’envoi du planning ; la première réponse s’engage à l’envoyer.', 'intent'),
('Which applicant has the most relevant experience?', 'Have a look at Jordan’s résumé.|The application is blue.|Experience takes time.', 'La référence au CV de Jordan répond indirectement à which applicant. Les autres ne désignent aucun candidat.', 'intent'),
('Where are the spare keys kept?', 'In the locked cabinet.|I have no time to spare.|The keynote starts at noon.', 'Where demande un lieu. Spare et key dans les autres propositions sont des pièges lexicaux.', 'detail'),
('Will the presentation be recorded?', 'You will be able to watch it later.|The record was broken.|Present it at the front desk.', 'Pouvoir revoir la présentation implique un enregistrement. Les distracteurs détournent record et present.', 'inference'),
('How did the customer hear about our service?', 'Through a recommendation from a colleague.|The service starts at ten.|I could not hear the announcement.', 'How demande ici le canal de découverte. La recommandation est ce canal.', 'detail'),
('Should we take the stairs or wait for the elevator?', 'We are only going up one floor.|The stairs were cleaned.|The weight is printed on the box.', 'Réponse indirecte favorisant les escaliers : un seul étage. Weight est un piège sonore pour wait.', 'intent'),
('Why is the lobby so crowded today?', 'A conference is taking place upstairs.|The crowd left early.|Yes, the lobby is open.', 'La conférence explique l’affluence. Les autres ne donnent pas de cause cohérente.', 'detail'),
('Have you signed up for the training session?', 'There were no places left.|The sign is outside.|The train leaves soon.', 'L’absence de places explique une impossibilité de s’inscrire. Sign et train sont repris avec un sens différent.', 'intent'),
('Who can authorize this expense?', 'Only the finance manager.|It is quite expensive.|We spent two hours there.', 'Who demande la personne habilitée, ici le responsable financier.', 'detail'),
('Would you mind turning down the music?', 'Of course, I will lower the volume.|I turned down the offer.|The musician lives nearby.', 'La demande porte sur le volume. La bonne réponse accepte l’action ; turning down an offer serait refuser.', 'intent'),
('When is the last day to register?', 'Applications close this Friday.|The register is broken.|It lasted a whole day.', 'La clôture vendredi donne l’échéance. Register et last dans les autres options prennent d’autres sens.', 'detail'),
('Did the interview go as planned?', 'It ran a little longer than expected.|The plan is in the folder.|We viewed the building.', 'La durée dépassée répond au déroulement de l’entretien. Les autres ne commentent pas l’interview.', 'inference'),
('Can the repair wait until Monday?', 'The machine is essential for today’s shift.|Monday is my day off.|I repaired it last year.', 'Le caractère indispensable pour aujourd’hui implique que l’intervention ne peut pas attendre.', 'inference'),
]
for i, (stem, opts, reason, skill) in enumerate(RESPONSES):
    add(f'p2-{i+1:03}', 2, 'Réponses directes et implicites', [q(stem, opts, reason, skill)], transcript=stem, accent=['US', 'UK', 'AU'][i % 3])

# The accompanying original photo atlas is generated specifically for these six items.
PHOTOS = [
('An empty meeting room', 'Chairs are arranged around a table.|People are cleaning the windows.|A woman is writing on a board.|The table is being carried outside.', 'Les chaises sont disposées autour d’une table. Aucune personne n’est visible ; aucune action en cours ne peut être affirmée.'),
('A warehouse worker', 'A worker is pushing a cart loaded with boxes.|A worker is climbing a ladder.|The shelves are being painted.|Two people are shaking hands.', 'Le travailleur pousse un chariot chargé. Les autres actions ne sont pas visibles.'),
('A café counter', 'A woman is pouring coffee into a cup.|A woman is washing a window.|A customer is opening an umbrella.|A chef is cutting vegetables.', 'Le geste visible est de verser du café. Attention à ne pas inventer une action simplement plausible dans un café.'),
('A train platform', 'Passengers are waiting beside a train.|A train is crossing a bridge.|The platform is completely empty.|People are repairing the tracks.', 'Des voyageurs attendent près du train. Rien n’indique un pont, un quai vide ou des travaux.'),
('An office desk', 'A laptop is next to a stack of books.|A man is carrying a desk.|Books are scattered across the floor.|The computer is being repaired.', 'L’ordinateur portable est près d’une pile de livres. La photo ne montre ni déplacement ni réparation.'),
('A garden walkway', 'A gardener is watering plants.|A gardener is cutting down a tree.|Cars are parked along a highway.|Someone is painting a fence.', 'L’action représentée est l’arrosage. Les autres activités ne sont pas visibles.'),
]
for i, (title, opts, reason) in enumerate(PHOTOS):
    add(f'p1-{i+1:03}', 1, 'Observation de photographie', [q('Choose the statement that best describes the photograph.', opts, reason, 'visual', 'B1')], image=i, accent=['US', 'UK', 'AU'][i % 3])

CONVERSATIONS = [
('A delayed delivery', [
 'Hi, this is Lena from Parkside Furniture. I am calling about the desks we ordered for our new office. They were supposed to arrive this morning.',
 'I am sorry. Our truck broke down just outside the city. We can send a replacement vehicle, but the delivery will not reach you until tomorrow afternoon.',
 'That is a problem. Our staff are moving in tomorrow morning. Could you at least send the meeting tables separately?',
 'Those are at our local warehouse. I can arrange for a van to bring them over before five today.'
 ], [('Why is Lena calling?', 'To ask about an order|To cancel a lease|To apply for a position|To book a repair', 'Elle s’enquiert des bureaux commandés et non livrés.', 'intent'), ('What caused the delay?', 'A vehicle problem|A missing payment|A shortage of staff|An incorrect address', 'Le camion est tombé en panne : truck broke down.', 'detail'), ('What will arrive first?', 'The meeting tables|The desks|The office chairs|The replacement truck', 'Le fournisseur propose de livrer les tables aujourd’hui avant cinq heures ; les bureaux arriveront demain.', 'inference')]),
('A conference booking', [
 'I need a room for our annual conference on May twelfth. We expect about sixty guests and will need a projector.',
 'Our Cedar Room holds fifty, and the Maple Room holds eighty. The larger room has all the equipment you mentioned. Would you like lunch included?',
 'Just coffee and light refreshments, please. Most participants will go to restaurants nearby. Could you email me a quotation?',
 'Certainly. I will include the room rental and the refreshment package. We can hold the room for three days while you decide.'
 ], [('What are the speakers arranging?', 'A business event|A restaurant opening|A staff interview|A flight reservation', 'Ils organisent la conférence annuelle.', 'intent'), ('Which room suits the group?', 'The Maple Room|The Cedar Room|Either room|Neither room', 'Soixante invités dépassent les cinquante places de Cedar. Maple accueille quatre-vingts personnes.', 'inference'), ('What does the caller request?', 'A written price estimate|A full lunch menu|A guest list|A revised invoice', 'Email me a quotation signifie envoyer un devis.', 'vocabulary')]),
('A revised schedule', [
 'Have you seen the new project schedule? The client moved the demonstration from Thursday to Tuesday.',
 'Tuesday? That only gives us two days to finish the interface. I can complete the main screen, but the reporting tool will not be ready.',
 'I spoke to the client. They only need to see the main screen at this stage. We can show the reporting tool at next month’s review.',
 'That is a relief. I will focus on the main screen and send you a working version tomorrow evening.'
 ], [('What changed?', 'The demonstration date|The project budget|The office location|The client’s address', 'La démonstration passe de jeudi à mardi.', 'detail'), ('Why does the second speaker say “That is a relief”?', 'Less work is required for the demonstration|The project has been cancelled|A new employee has joined|The deadline has been extended', 'Le client n’exige que l’écran principal ; la charge immédiate diminue malgré l’échéance avancée.', 'intent'), ('What will the second speaker do tomorrow?', 'Send a working version|Present the reporting tool|Visit the client|Prepare a contract', 'Il promet une version opérationnelle pour demain soir.', 'detail')]),
('A missing receipt', [
 'I am filling out my travel expense form, but I cannot find the receipt for my taxi from the airport.',
 'Do you have the booking confirmation in your email? The finance team accepts that if it shows the amount paid.',
 'Yes, I booked through an app, so I should be able to download it. Is there a deadline for submitting this month’s expenses?',
 'Friday at noon. Anything received after that will be reimbursed next month. Be sure to attach the train tickets as well.'
 ], [('What problem does the first speaker have?', 'A receipt is missing|A flight was cancelled|A payment was rejected|A phone is broken', 'La personne ne retrouve pas son reçu de taxi.', 'detail'), ('What alternative is suggested?', 'An email booking confirmation|A letter from the airport|A bank loan application|A handwritten map', 'La confirmation est acceptée si elle affiche le montant payé.', 'detail'), ('What happens if the form is late?', 'Payment is deferred to the following month|The expense is permanently rejected|A fee is charged|A manager must travel', 'Les dépenses reçues après vendredi midi seront remboursées le mois suivant.', 'inference')]),
('A product display', [
 'Maya, could you help me arrange the front window? The new spring collection arrived this morning, and I want it on display before we open tomorrow.',
 'Of course. Should we use the wooden stands from the storeroom?',
 'Yes, but we need to move the winter items first. Put them near the back of the shop, beside the discounted accessories.',
 'I will take care of that now. Do you want price tags on everything?',
 'Definitely. The new labels are in the drawer under the register.'
 ], [('Where are the speakers most likely working?', 'In a retail shop|In a hospital|At an airport|At a factory', 'Vitrine, collection saisonnière et caisse renvoient à un magasin.', 'inference'), ('What should Maya do first?', 'Move the winter items|Print a catalogue|Order new stands|Clean the windows', 'Move the winter items first donne explicitement la priorité.', 'detail'), ('Where are the labels?', 'Under the register|Beside the entrance|In the storeroom|On the window', 'Les étiquettes se trouvent dans le tiroir sous la caisse.', 'detail')]),
('A maintenance visit', [
 'The air conditioning in our training room has stopped working. We have a full-day workshop tomorrow, so it is quite urgent.',
 'I can send a technician between two and four this afternoon. Is someone available to let them in?',
 'I have a meeting at two, but our receptionist will be here. Should I ask her to show them the control panel?',
 'Yes, please. Also, ask her not to reset the system again. That could erase the error code the technician needs to diagnose the fault.'
 ], [('What needs attention?', 'A cooling system|A security camera|A projector|A telephone line', 'Air conditioning désigne la climatisation.', 'vocabulary'), ('Who will meet the technician?', 'The receptionist|The workshop instructor|The caller’s client|The finance manager', 'Le réceptionniste sera présent pendant la réunion de l’appelant.', 'detail'), ('Why should the system not be reset?', 'Useful diagnostic information could be lost|The warranty has expired|The electricity bill would rise|The workshop has been cancelled', 'Une réinitialisation pourrait effacer le code d’erreur nécessaire au diagnostic.', 'inference')]),
('A job interview', [
 'Thank you for coming in, Alex. Your application mentions five years in customer support. What made you interested in our account management role?',
 'I enjoy building long-term relationships with clients. In my current job, I usually solve one problem and then move on. I would like to follow projects from beginning to end.',
 'That fits what we need. The position involves some travel, usually one week each month. Would that be manageable?',
 'Yes. Could you tell me more about the training programme for new account managers?'
 ], [('What is the purpose of the conversation?', 'To discuss a job application|To resolve a billing dispute|To review a travel policy|To renew a service contract', 'L’interlocuteur évalue la candidature d’Alex.', 'intent'), ('What motivates Alex?', 'Developing lasting client relationships|Avoiding all travel|Working fewer hours|Changing to a technical occupation', 'Alex souhaite suivre les clients et projets dans la durée.', 'detail'), ('What does Alex ask about?', 'Initial staff training|Monthly sales targets|Annual leave|Office parking', 'La dernière question porte sur le programme de formation des nouveaux responsables.', 'detail')]),
('A catering change', [
 'We have just received the final guest list for Friday’s reception. There are now forty-eight people, six more than we expected.',
 'That should not be a problem. Do the additional guests have any dietary requirements?',
 'Two are vegetarian, and one cannot eat nuts. Could you label the dishes clearly?',
 'Absolutely. I will update the menu and send it this afternoon. The total will increase, but the delivery charge will stay the same.'
 ], [('How many guests were originally expected?', 'Forty-two|Forty-eight|Fifty-four|Thirty-six', '48 invités désormais, soit 6 de plus : 48 − 6 = 42.', 'inference'), ('What does the customer request?', 'Clear food labels|An earlier delivery|Extra tables|A different venue', 'Le client demande d’étiqueter clairement les plats pour les restrictions alimentaires.', 'detail'), ('What will remain unchanged?', 'The delivery fee|The number of guests|The menu|The total price', 'La livraison conserve son prix ; le total augmente.', 'detail')]),
('A museum visit', [
 'I am organising a visit for twelve colleagues. Is the photography exhibition included in the general admission ticket?',
 'It requires a separate ticket. However, groups of ten or more receive a twenty percent discount on both tickets if they book online.',
 'Good to know. Is there a guided tour in the afternoon?',
 'There is one at two thirty, but it is nearly full. The four o’clock tour has plenty of space. You should reserve soon because weekends are busy.'
 ], [('What is true about the exhibition?', 'A separate ticket is required|It is closed on weekends|It is only for groups|It has no admission fee', 'L’exposition photo nécessite un billet distinct.', 'detail'), ('Why does the group qualify for a discount?', 'It has at least ten members|It is visiting in the morning|It consists of museum staff|It booked last month', 'Douze participants dépassent le seuil de dix.', 'inference'), ('Which tour has more availability?', 'The four o’clock tour|The two thirty tour|The morning tour|The evening tour', 'Le guide indique plenty of space à seize heures.', 'detail')]),
('A shared workspace', [
 'I tried to reserve a desk for Wednesday, but the booking system shows every space as unavailable.',
 'The east wing is being repainted. We are using the meeting rooms as temporary workspaces. You can reserve one through reception.',
 'I have several video calls that day. Will the meeting rooms be quiet enough?',
 'Room six is being kept as a quiet zone. Ask for a place there. The other rooms are open for collaborative work.'
 ], [('Why are the usual desks unavailable?', 'Part of the building is being decorated|A conference is taking place|The company is moving permanently|The internet is down', 'L’aile est est en cours de peinture.', 'detail'), ('How should a space be booked?', 'Through reception|By contacting the painters|On the public website|By calling a client', 'Les places temporaires se réservent auprès de l’accueil.', 'detail'), ('Why is room six recommended?', 'It is reserved for quiet work|It has the largest table|It is closest to the exit|It has new furniture', 'Les visioconférences nécessitent le calme offert par la quiet zone.', 'inference')]),
('A revised train journey', [
 'Our meeting in York starts at eleven. I was planning to take the nine o’clock express.',
 'That service has been cancelled. I checked the timetable: the eight thirty train arrives at ten fifteen, and the nine thirty arrives at eleven twenty.',
 'Then we will have to take the earlier one. Shall I book the tickets for both of us?',
 'Please do. I will email the client to confirm we will be there on time. We should allow fifteen minutes for the walk from the station.'
 ], [('What happened to the planned train?', 'It was cancelled|It departed early|Its fare increased|It changed platform', 'Le service initial de neuf heures est supprimé.', 'detail'), ('Which departure will they choose?', 'Eight thirty|Nine o’clock|Nine thirty|Eleven twenty', 'Seul le départ de 8 h 30 permet d’arriver avant la réunion de 11 h.', 'inference'), ('What will the second speaker do?', 'Contact the client|Purchase both tickets|Drive to York|Cancel the meeting', 'La deuxième personne va envoyer un courriel au client.', 'detail')]),
('Choosing a supplier', [
 'We need three hundred notebooks for the conference next Friday. Which supplier can meet that deadline?',
 'North Paper can deliver on Wednesday, but their minimum order is five hundred. Green Print can deliver on Thursday and accepts orders from two hundred.',
 'What about City Stationery?',
 'They cannot deliver until the following Monday. Green Print seems the best fit, even though their unit price is a little higher.',
 'Agreed. Please place the order today and request our logo on the cover.'
 ], [('How many notebooks are needed?', 'Three hundred|Two hundred|Five hundred|One hundred', 'Le besoin annoncé est de trois cents carnets.', 'detail'), ('Why is North Paper unsuitable?', 'Its minimum order is too large|Its delivery is too late|It cannot print logos|Its paper is unavailable', 'La commande minimale est de cinq cents, au-delà du besoin de trois cents.', 'inference'), ('What additional feature is requested?', 'A company logo on the cover|Individual gift wrapping|Numbered pages|A leather binding', 'La dernière réplique demande le logo sur la couverture.', 'detail')]),
('Three colleagues plan a launch', [
 'Nora: The launch event is on Friday. I have confirmed the venue, but we still need someone to greet the guests.',
 'Ben: I can do that. I will arrive an hour early and set up the registration table. Amira, are the presentation slides ready?',
 'Amira: Almost. I am waiting for the latest sales figures from finance. They promised to send them by three today.',
 'Nora: Great. Once the slides are finished, send them to me for a final check. Ben, please bring the printed name badges with you.'
 ], [('What has Nora already arranged?', 'The venue|The name badges|The final slides|The sales figures', 'Nora a déjà confirmé le lieu de l’événement ; les badges et les diapositives relèvent des autres participants.', 'detail'), ('What will Ben do at the event?', 'Welcome attendees|Give the main presentation|Prepare the catering|Take photographs', 'Ben se charge d’accueillir les invités et de la table d’inscription.', 'detail'), ('What is Amira waiting for?', 'Updated financial data|A room confirmation|A guest list|A printing quotation', 'Amira attend les derniers chiffres de ventes du service financier.', 'detail')]),
]
for i, (title, dialogue, items) in enumerate(CONVERSATIONS):
    add(f'p3-{i+1:03}', 3, title, [q(*item) for item in items], transcript='\n\n'.join(dialogue), dialogue=dialogue, accent=['US','UK','AU'][i % 3])

TALKS = [
('A building announcement', 'Attention all staff. The main entrance will be closed tomorrow morning while the automatic doors are replaced. Please use the side entrance on Oak Street. Security staff will be there to check your identification badges. Visitors should report to the temporary reception desk in the ground-floor meeting room. The work is expected to finish by noon, but we will send an email once the main entrance is open again. Deliveries should continue to use the loading bay at the rear of the building.', [
 ('Why will the entrance be closed?', 'Doors are being replaced|A meeting is being held|Badges are being distributed|The building is being sold', 'Le remplacement des portes automatiques motive la fermeture.', 'detail'), ('Where should visitors go?', 'To a ground-floor meeting room|To the loading bay|To the second-floor office|To the main entrance', 'La réception temporaire se trouve dans la salle de réunion du rez-de-chaussée.', 'detail'), ('How will staff learn that work is finished?', 'By email|By a phone call|From a newspaper|From a printed ticket', 'Un courriel annoncera la réouverture.', 'detail')]),
('A voicemail about an appointment', 'Hello, Mr. Lewis. This is Priya from Westside Dental. I am calling about your appointment with Dr. Harris on Thursday at ten. Unfortunately, the doctor needs to attend an urgent meeting, so we need to reschedule. We have an opening at two on the same afternoon, or at nine on Friday morning. Please call us before five today to let us know which time you prefer. If neither option works, we can look at dates next week. There is no charge for changing this appointment.', [
 ('Why is Priya calling?', 'To change an appointment|To request payment|To confirm an address|To discuss treatment results', 'Le médecin est indisponible au créneau initial ; il faut déplacer le rendez-vous.', 'intent'), ('What time is offered on Thursday?', 'Two in the afternoon|Ten in the morning|Nine in the morning|Five in the afternoon', 'Thursday at two est proposé ; Friday at nine est l’autre option.', 'detail'), ('What is the listener asked to do?', 'Call back today|Visit the clinic immediately|Pay a cancellation fee|Send medical records', 'La personne doit rappeler avant dix-sept heures aujourd’hui.', 'detail')]),
('A staff induction', 'Welcome to your first day at Harbor Logistics. We will begin with a short tour of the warehouse, followed by a safety briefing in the training room. Please wear the high-visibility vests you were given at reception whenever you enter the storage area. After lunch, you will meet your team supervisors and receive your shift schedules. If you have not yet submitted your bank details, please bring them to the personnel office before you leave today so that your first salary payment is not delayed.', [
 ('Who is the talk intended for?', 'New employees|Delivery customers|External auditors|Job applicants', 'Le discours accueille les salariés pour leur premier jour.', 'inference'), ('What must be worn in the storage area?', 'A high-visibility vest|A formal jacket|A visitor’s hat|A name sticker only', 'Le gilet haute visibilité est requis dans la zone de stockage.', 'detail'), ('Why are bank details requested?', 'To process salary payments|To arrange a loan|To charge for equipment|To issue travel tickets', 'Les coordonnées bancaires évitent de retarder le premier salaire.', 'detail')]),
('A radio advertisement', 'Looking for a flexible place to work? River Desk has just opened beside the central station. Our bright shared workspace offers high-speed internet, private call booths, and meeting rooms. Day passes cost twenty-five pounds, while monthly members can access the building at any time. To celebrate our opening, your first day is free when you book through our website before the end of this month. Coffee and printing are included. Visit River Desk online to reserve a tour and discover a better way to work.', [
 ('What is being advertised?', 'A shared workspace|A coffee delivery service|A railway ticket|A printing company', 'Bureaux partagés, cabines et salles de réunion caractérisent un espace de coworking.', 'intent'), ('What benefit do monthly members receive?', 'Access at any time|Free rail travel|Unlimited guest tickets|A personal computer', 'Les membres mensuels ont accès au bâtiment à toute heure.', 'detail'), ('How can someone obtain a free first day?', 'Book online before the month ends|Buy ten day passes|Visit with a colleague|Call the station', 'L’offre requiert une réservation sur le site avant la fin du mois.', 'detail')]),
('A factory update', 'Good morning. I have some news about the packaging line upgrade. Installation was completed over the weekend, but we still need to run quality checks before full production resumes. Today, the morning shift will attend training with the equipment supplier. The afternoon shift will help test sample batches. We expect normal operations to restart on Wednesday. Until then, urgent orders will be handled by our other facility in Brighton. Please direct any customer enquiries about delivery dates to the sales office.', [
 ('What has already been completed?', 'Installation of new equipment|All quality checks|Staff training|The transfer of every order', 'L’installation s’est terminée pendant le week-end ; les contrôles restent à faire.', 'detail'), ('What will the morning shift do?', 'Attend training|Ship sample batches|Travel to Brighton|Contact every customer', 'L’équipe du matin suit la formation du fournisseur.', 'detail'), ('Who should handle delivery enquiries?', 'The sales office|The equipment supplier|The afternoon shift|The security team', 'Les demandes de dates de livraison doivent être adressées au service commercial.', 'detail')]),
('A guided tour', 'We are now entering the oldest part of the botanical garden. The glasshouse on your left was built in eighteen ninety and originally housed tropical fruit trees. Today it contains our orchid collection. Unfortunately, it is closed for maintenance this week, but you can see photographs of the collection in the visitor centre. Our next stop is the herb garden, where you will have ten minutes to explore on your own. Please stay on the marked paths, as some of the plants are part of a research project.', [
 ('What is currently in the glasshouse?', 'Orchids|Tropical fruit trees|Herbs|Historical tools', 'Les arbres fruitiers étaient présents à l’origine ; aujourd’hui ce sont des orchidées.', 'detail'), ('Why can visitors not enter?', 'Maintenance is taking place|A private event is being held|Tickets have sold out|The collection has moved', 'La fermeture cette semaine est due à la maintenance.', 'detail'), ('What are visitors told to do?', 'Keep to marked paths|Pick herbs for a study|Leave within ten minutes|Buy a separate ticket', 'Rester sur les chemins protège notamment les plantes étudiées.', 'detail')]),
('An airport announcement', 'Passengers travelling on flight seven twenty to Oslo, please note that your departure gate has changed from gate twelve to gate eighteen. Boarding will begin in twenty minutes. The flight is still scheduled to depart at fourteen forty-five. Passengers who require assistance should make themselves known to a member of staff at the new gate. Please have your boarding pass and identification ready. We apologise for the inconvenience and thank you for your patience.', [
 ('What has changed?', 'The departure gate|The destination|The flight number|The departure time', 'Seule la porte change ; l’horaire est maintenu.', 'detail'), ('Which gate should passengers use?', 'Eighteen|Twelve|Twenty|Seven', 'La nouvelle porte est eighteen, soit dix-huit.', 'detail'), ('Who should contact a staff member?', 'Passengers needing assistance|All passengers with luggage|Only business travellers|Passengers arriving from Oslo', 'Les voyageurs ayant besoin d’assistance sont invités à se signaler.', 'detail')]),
('A sales presentation', 'Thank you for joining this quarterly review. As you can see in the chart, our online store had its strongest month in March. The new website launched in February, but the advertising campaign did not begin until March, which likely contributed to the increase. Store sales remained stable throughout the period. Next quarter, we will test a loyalty programme for online customers. Before expanding it, we will compare repeat purchases with those from customers who are not enrolled. I will send the detailed proposal after this meeting.', [
 ('Look at the graphic. What were online sales in the strongest month?', '$48,000|$32,000|$35,000|$41,000', 'L’audio identifie mars ; le tableau associe mars à 48 000 dollars.', 'visual'), ('What began in March?', 'An advertising campaign|A website redesign|A store closure|A loyalty programme', 'La publicité démarre en mars ; le site a été lancé en février.', 'detail'), ('What will be evaluated next quarter?', 'A customer loyalty initiative|A new warehouse|A staff bonus scheme|A delivery vehicle', 'Le programme de fidélité sera testé sur les achats répétés.', 'detail')]),
('A community notice', 'The Riverside Library is introducing extended opening hours from next Monday. We will now close at eight in the evening on weekdays, two hours later than before. Weekend hours will remain unchanged. The additional time will allow students and people who work during the day to use our study rooms and computers. Please remember that the children’s section will still close at six. We are also looking for volunteers to help with our Saturday reading group. Application forms are available at the information desk.', [
 ('At what time did the library previously close on weekdays?', 'Six in the evening|Eight in the evening|Four in the afternoon|Ten at night', 'La fermeture devient 20 h, deux heures plus tard qu’avant : ancien horaire 18 h.', 'inference'), ('What will remain unchanged?', 'Weekend hours|Weekday closing time|All study room access|Computer availability in the evening', 'Le discours précise que les horaires du week-end ne changent pas.', 'detail'), ('Where can volunteers get an application?', 'At the information desk|On a bus|At the university|Inside every book', 'Les formulaires sont disponibles au bureau d’information.', 'detail')]),
('A project handover', 'Before I leave for annual leave tomorrow, I want to clarify the arrangements for the Benton project. Sofia will be your main contact for technical questions. Mark will handle budget approvals, but any expense above two thousand euros still needs the director’s signature. The client review has been moved to the eighteenth, giving us an extra week to prepare. Please upload your progress reports by Tuesday afternoon so Sofia can combine them. I will have limited access to email, so contact the team directly if anything urgent comes up.', [
 ('Who will handle technical questions?', 'Sofia|Mark|The director|The client', 'Sofia devient le contact technique principal.', 'detail'), ('What requires the director’s signature?', 'An expense of more than €2,000|Every technical question|All weekly reports|Any holiday request', 'L’autorisation du directeur reste nécessaire au-dessus de 2 000 euros.', 'detail'), ('What does the changed review date allow?', 'More preparation time|An earlier holiday|A smaller project team|Immediate budget approval', 'Le déplacement de la revue donne une semaine supplémentaire de préparation.', 'inference')]),
]
for i, (title, script, items) in enumerate(TALKS):
    extra = {'graphic': {'headers': ['Month', 'Online sales'], 'rows': [['January', '$32,000'], ['February', '$35,000'], ['March', '$48,000'], ['April', '$41,000']]}} if i == 7 else {}
    add(f'p4-{i+1:03}', 4, title, [q(*item) for item in items], transcript=script, accent=['UK','US','AU'][i % 3], **extra)

CLOZE = [
('Office relocation', 'To: All staff\nSubject: Moving to our new office\n\nWe are pleased to announce that our team will move to the Riverside building on 3 June. The new premises are considerably [1] than our current office and include two additional meeting rooms.\n\nAll personal belongings must be packed [2] Friday afternoon. The removal company will transport the boxes over the weekend. [3]\n\nIf you have any questions, please contact the facilities team. We appreciate your [4] during the transition.', [
 ('[1]', 'larger|largest|largely|large', 'Than impose le comparatif larger. Largest est superlatif ; largely adverbe ; large n’a pas de marque comparative.', 'agreement'),
 ('[2]', 'by|since|during|among', 'By marque la date limite de l’emballage. Since marque un début passé ; during une période ; among un ensemble.', 'prepositions'),
 ('[3]', 'Please label each box with your name and department.|The building was sold to a private investor.|We have decided to cancel the relocation.|The cafeteria menu will be updated next year.', 'L’étiquetage prolonge logiquement les consignes d’emballage et de transport. Les autres phrases sont hors sujet ou contredisent le déménagement.', 'inference'),
 ('[4]', 'cooperation|cooperate|cooperative|cooperatively', 'Your est suivi du nom cooperation. Les autres formes sont verbe, adjectif et adverbe.', 'word-forms')]),
('Supplier update', 'Dear Ms. Morgan,\n\nThank you for your recent order. We regret to inform you that the model you selected is [1] unavailable. We expect a new shipment early next month.\n\n[2], we can offer the upgraded model at the same price. It includes a longer battery life and is fully compatible [3] your existing accessories. [4]\n\nPlease let us know which option you prefer by Wednesday so that we can arrange delivery promptly.\n\nYours sincerely,\nOwen Reed, Customer Support', [
 ('[1]', 'temporarily|temporary|temporariness|temporal', 'Temporarily modifie unavailable. Temporary/temporal sont adjectifs ; temporariness est un nom.', 'word-forms'),
 ('[2]', 'Alternatively|Nevertheless|Consequently|Similarly', 'Alternatively introduit une solution de remplacement au modèle indisponible. Les autres liens ne décrivent pas cette fonction.', 'connectors'),
 ('[3]', 'with|at|from|over', 'La collocation attendue est compatible with.', 'prepositions'),
 ('[4]', 'This replacement can be dispatched within two business days.|Your account has been permanently closed.|Our store no longer sells electronic products.|The invoice you requested last year is missing.', 'La phrase complète l’offre alternative avec un délai de livraison. Les distracteurs rompent la cohérence.', 'inference')]),
('Training invitation', 'To: Department heads\nSubject: Data protection workshop\n\nA practical workshop on data protection [1] in the training room next Tuesday. Participants will learn how to identify suspicious messages and store customer information securely.\n\nManagers are encouraged [2] at least one representative from each team. [3]\n\nPlaces are limited, so early [4] is recommended. To reserve a place, complete the online form by this Friday.', [
 ('[1]', 'will be held|held|has holding|holding', 'Le futur passif will be held convient à un atelier qui aura lieu mardi prochain. Les autres formes sont incomplètes ou incorrectes.', 'tenses'),
 ('[2]', 'to nominate|nominating|nominate|nominated', 'Be encouraged to + infinitif : to nominate. Les autres formes ne complètent pas ce passif.', 'agreement'),
 ('[3]', 'Those attending should share the key points with their colleagues afterward.|The office furniture was replaced last winter.|The workshop has been cancelled due to lack of interest.|All customer records will be published online.', 'Le partage des acquis justifie l’envoi d’un représentant par équipe. Les autres phrases sont étrangères au propos ou contradictoires.', 'inference'),
 ('[4]', 'registration|register|registered|registering of', 'Early qualifie ici le nom registration. Les autres formes ne forment pas le groupe nominal attendu.', 'word-forms')]),
('A service notice', 'Dear members,\n\nOur online booking system will be unavailable from 10 p.m. on Saturday until 6 a.m. on Sunday [1] essential maintenance. Reservations made before the shutdown will not be [2].\n\n[3]\n\nOnce the update is complete, you will notice a simpler layout and a new option for recurring bookings. [4] you encounter any problems, please contact our support team.\n\nThank you for your patience.', [
 ('[1]', 'because of|although|unless|even though', 'Because of + nom exprime la cause. Les autres conjonctions exigent ici une proposition.', 'connectors'),
 ('[2]', 'affected|effected|affecting|effective', 'Be affected signifie être affecté. Effected signifie effectué, affecting est actif, effective adjectif.', 'vocabulary'),
 ('[3]', 'During this period, urgent reservations can be made by calling reception.|We recommend deleting all existing reservations.|The maintenance was completed last year.|Members are no longer permitted to book online.', 'La solution téléphonique répond à l’indisponibilité temporaire. Les autres phrases contredisent le contexte.', 'inference'),
 ('[4]', 'Should|Had|Would|Were', 'Should you encounter est une condition formelle : si vous rencontrez. Had demanderait encountered ; were ne se combine pas ainsi ; would est inadapté.', 'agreement')]),
]
for i, (title, body, items) in enumerate(CLOZE):
    add(f'p6-{i+1:03}', 6, title, [q(*x) for x in items], documents=[{'title': title, 'body': body}])

READINGS = [
('A returned order', 'Email · Hartwell Office Supplies', 'To: Jamie Bell\nSubject: Return request #418\n\nThank you for contacting us about the desk lamp you received on 8 September. We are sorry that its base was damaged in transit. A replacement has already been dispatched and should arrive within three business days.\n\nPlease use the prepaid label attached to this message to return the damaged item within fourteen days. You do not need the original packaging, but please use a sturdy box. If the replacement does not arrive by Friday, contact us with your order number.\n\nKind regards,\nElena Woods\nCustomer Care', [
 ('Why was the email sent?', 'To explain a replacement procedure|To advertise a new lamp|To reject a refund request|To confirm a store opening', 'Le message annonce un remplacement et les modalités de retour.', 'intent'),
 ('What must Jamie do?', 'Send back the damaged lamp|Pay for a new lamp|Visit a physical store|Find the original box', 'La lampe abîmée doit être renvoyée sous quatorze jours ; le carton d’origine n’est pas obligatoire.', 'detail'),
 ('What can be inferred about the return?', 'Postage has already been paid|It must be delivered in person|It is optional|It will take three business days', 'Prepaid label indique une étiquette d’expédition prépayée. Les trois jours concernent le remplacement.', 'inference')]),
('A workspace policy', 'Notice · Quiet-zone guidelines', 'From 1 November, the second-floor study area will be designated a quiet zone. Phone calls and online meetings should take place in the booths near the lifts. Desks in the quiet zone cannot be reserved and are available on a first-come, first-served basis.\n\nFood is not permitted, although drinks in sealed containers are welcome. Please remove your belongings if you leave for more than thirty minutes so that others can use the space.\n\nThese changes follow feedback from members who need an uninterrupted environment for focused work. Group tables remain available on the ground floor.', [
 ('Why is the policy being introduced?', 'Members requested a quieter environment|The second floor is being repaired|The building has fewer desks|Food prices have increased', 'La dernière partie attribue le changement aux retours des membres.', 'intent'),
 ('Which activity is permitted in the quiet zone?', 'Drinking from a sealed bottle|Holding a video meeting|Reserving a desk|Eating a sandwich', 'Les boissons dans des récipients fermés sont autorisées ; les trois autres actions sont exclues.', 'detail'),
 ('What should someone leaving for an hour do?', 'Take their belongings with them|Leave a reservation sign|Ask the lift operator|Move a table downstairs', 'Une absence supérieure à trente minutes impose de libérer l’espace.', 'inference')]),
('A job advertisement', 'Careers · Visitor services coordinator', 'The Eastbank Arts Centre seeks a visitor services coordinator to manage its front desk and supervise a team of part-time assistants. The successful applicant will have at least two years of customer-facing experience and excellent organisational skills. Knowledge of another language is desirable but not essential.\n\nThe position is full-time and includes some evening and weekend shifts. In return, we offer a competitive salary, training opportunities and complimentary admission to centre events.\n\nSend a CV and a covering letter to careers@eastbank.example by 12 March. Shortlisted candidates will be invited to interviews in the final week of March.', [
 ('What is a requirement for the role?', 'Two years of relevant experience|Fluency in three languages|An arts degree|Experience as a curator', 'Deux ans d’expérience avec la clientèle sont exigés ; une autre langue n’est que souhaitée.', 'detail'),
 ('What benefit is offered?', 'Free entry to events|Free housing|Only weekday shifts|A company car', 'Complimentary admission signifie accès gratuit aux événements.', 'vocabulary'),
 ('When will interviews take place?', 'Near the end of March|On 12 March|At the start of April|Every weekend', 'Final week of March désigne la dernière semaine du mois.', 'detail')]),
('A hotel review', 'Review · The Linden Hotel', 'I stayed at the Linden Hotel for a three-day conference. Its location, five minutes from the station, made arrival easy. The room was spotless, and the staff arranged an early breakfast when our first session started at seven.\n\nThe only drawback was the unreliable wireless internet in my room. The connection worked well in the lobby, but that was inconvenient when I needed to join a private call. The manager said the network would be upgraded next month.\n\nI would happily return once that work is complete. Business travellers should check the status of the upgrade before booking.', [
 ('What does the reviewer praise?', 'The staff’s flexibility|The in-room internet|The conference speakers|The size of the swimming pool', 'Le personnel a organisé un petit-déjeuner anticipé pour répondre au besoin.', 'detail'),
 ('What does “drawback” mean in this review?', 'Disadvantage|Refund|Attraction|Discount', 'Drawback désigne le point négatif : le Wi-Fi instable.', 'vocabulary'),
 ('What is recommended to future guests?', 'Verify that the network work is finished|Avoid early breakfast|Arrive by car|Book a private lobby', 'Il est conseillé de vérifier l’état de la mise à niveau avant de réserver.', 'inference')]),
('A team chat', 'Chat · Product launch', '09:10 — Sam: The print shop says the brochures will be ready on Thursday, not Wednesday.\n09:12 — Leila: Our event starts Friday morning. Can we collect them ourselves? Courier delivery might take too long.\n09:14 — Sam: Yes, collection is possible after 3 p.m. I have a client meeting then.\n09:16 — Ravi: I will be near the print shop on Thursday afternoon. Send me the order reference and I can pick them up.\n09:18 — Leila: Perfect. I will finish the digital version today so we have a backup.\n09:20 — Sam: Thanks, both. I will email the reference to Ravi now.', [
 ('What problem is discussed?', 'Printing will finish later than expected|The event venue is unavailable|The brochures contain an error|A client has cancelled', 'La mise à disposition des brochures glisse de mercredi à jeudi.', 'detail'),
 ('What will Ravi do?', 'Collect the brochures|Edit the digital version|Attend Sam’s meeting|Book a courier', 'Ravi propose de récupérer la commande à proximité.', 'detail'),
 ('Why will Leila prepare a digital version?', 'To have an alternative if needed|To cancel the print order|To change the event date|To avoid contacting Ravi', 'So we have a backup exprime une solution de secours.', 'inference')]),
('A software update', 'Release notes · ScheduleMate 4.2', 'Version 4.2 introduces shared calendar templates and improved reminders. Administrators can now create a standard weekly schedule and apply it to several teams at once. Individual staff members can still request changes, but those requests must be approved before they appear on the shared calendar.\n\nThe update also resolves an issue that caused duplicate email notifications. Existing schedules will be retained during installation.\n\nImportant: users running version 3.0 or earlier must first install version 4.0. Direct upgrades from those versions to 4.2 are not supported.', [
 ('What is a new feature?', 'Reusable schedules for multiple teams|Automatic approval of all requests|Unlimited free accounts|Replacement of every existing calendar', 'Les modèles hebdomadaires s’appliquent désormais à plusieurs équipes.', 'detail'),
 ('What must a version 3.0 user do first?', 'Install version 4.0|Delete all schedules|Create a new account|Disable email permanently', 'Le passage intermédiaire par la version 4.0 est obligatoire.', 'detail'),
 ('What problem has been fixed?', 'Repeated email notifications|Lost account passwords|Inaccurate salary calculations|Blocked internet access', 'Les notifications reçues en double sont corrigées.', 'detail')]),
('A restaurant notice', 'Notice · Terrace reservations', 'Our terrace will reopen on 15 April, weather permitting. Tables can be booked for groups of up to six guests. Larger parties are welcome in the main dining room, where a set menu is available for groups of eight or more.\n\nTerrace bookings are provisional until the morning of your visit. If poor weather prevents outdoor service, we will offer an indoor table where possible. We cannot guarantee indoor seating for every terrace reservation.\n\nPlease provide a mobile number when booking so we can contact you promptly. No deposit is required for terrace tables.', [
 ('Which group may reserve a terrace table?', 'Five guests|Seven guests|Eight guests|Ten guests', 'La terrasse accepte au maximum six personnes par groupe.', 'detail'),
 ('What is uncertain for terrace guests?', 'Whether an indoor table will be available in bad weather|Whether a deposit is refundable|Whether the restaurant has a main dining room|Whether mobile numbers are accepted', 'Un repli intérieur est proposé si possible, sans garantie de place.', 'inference'),
 ('Why is a mobile number requested?', 'To communicate changes quickly|To collect a deposit|To send a set menu automatically|To verify the size of the group', 'Le numéro sert à joindre rapidement le client si les conditions changent.', 'intent')]),
('A professional development fund', 'Memo · Learning allowance', 'Permanent employees may apply for up to €600 each calendar year toward an external course related to their current role. Applications must include a course description, the fee and a short explanation of how the learning will benefit the team.\n\nApproval must be obtained before enrolling. Reimbursement is made after the employee submits both a receipt and proof of attendance. Unused funds cannot be carried over to the following year.\n\nTeam leaders should review requests within ten working days. Courses required by the company are paid from a separate budget and do not reduce this allowance.', [
 ('What must happen before enrolment?', 'The request must be approved|A receipt must be submitted|The course must be completed|The next calendar year must begin', 'L’approbation précède l’inscription.', 'detail'),
 ('What happens to unused funds?', 'They expire at the end of the year|They double the next year|They are paid as salary|They fund compulsory courses', 'Cannot be carried over signifie que le reliquat n’est pas reporté.', 'inference'),
 ('What is true of company-required courses?', 'They use a different budget|They must cost under €600|They are paid by employees|They need no attendance', 'Les formations imposées utilisent un budget distinct.', 'detail')]),
('An invitation to tender', 'Procurement · Cleaning services', 'Northgate Business Park invites proposals for evening cleaning services across three office buildings. The contract will run for one year from 1 July, with a possible extension based on performance.\n\nInterested companies should attend the site visit on 6 May at 10 a.m. to assess the facilities. Written proposals must include staffing levels, environmental practices and a fixed monthly price. Submit all documents by 20 May at noon.\n\nThe lowest-priced proposal will not necessarily be selected. Reliability, staff training and sustainable methods will also be considered. Questions should be sent in writing by 13 May.', [
 ('What is the notice seeking?', 'A cleaning contractor|Office tenants|A construction supervisor|A furniture supplier', 'Il s’agit d’un appel d’offres pour le nettoyage en soirée.', 'intent'),
 ('What is the deadline for proposals?', '20 May at noon|6 May at 10 a.m.|13 May at noon|1 July at 10 a.m.', 'Ne pas confondre la visite du 6, les questions du 13 et la soumission du 20 mai.', 'detail'),
 ('What can be inferred about selection?', 'Quality may outweigh the lowest price|Price is the only criterion|Every bidder will receive a contract|The contract cannot be extended', 'Fiabilité, formation et durabilité comptent aussi : l’offre la moins chère n’est pas forcément retenue.', 'inference')]),
('A collection service', 'Service information · Click & collect', 'Orders placed before noon from Monday to Friday are normally ready for collection after 4 p.m. the same day. You will receive an email once your order is ready; please wait for that message before travelling to the store.\n\nBring your order confirmation and photo identification. If someone else collects for you, they must bring a copy of your confirmation and their own identification. Orders are held for seven days, after which they are cancelled and refunded.\n\nThis service is not available for refrigerated goods or items shipped directly by our partner suppliers.', [
 ('What should customers do before travelling to the store?', 'Wait for a readiness email|Call a partner supplier|Cancel refrigerated orders|Send a photograph', 'Le message de disponibilité doit être reçu avant le déplacement.', 'detail'),
 ('What happens after seven days without collection?', 'The order is cancelled and refunded|A storage fee is charged|The order is delivered automatically|The collection window becomes permanent', 'Les commandes non récupérées sont annulées et remboursées.', 'detail')]),
]
for i, (title, kind, body, items) in enumerate(READINGS):
    add(f'p7-s{i+1:02}', 7, title, [q(*x) for x in items], documents=[{'title': kind, 'body': body}], passage_type='single')

MULTI = [
('A conference reservation', [
 ('Offer · Willow Conference Centre', 'Room hire: Cedar, 40 guests, €400 per day; Maple, 80 guests, €650 per day. Both rooms include a projector. Refreshments cost €12 per person. Lunch is available for €24 per person. A 20% deposit on room hire confirms a booking. Cancellations fewer than seven days before an event forfeit the deposit.'),
 ('Email · Booking request', 'To: Willow Conference Centre\nWe would like to reserve the Maple Room for 60 people on 18 June. Please include refreshments but no lunch. Our accounts team will pay the deposit tomorrow. Please confirm that there is wheelchair access.\nBest regards,\nTina Cole'),
 ], [
 ('Why is the Maple Room appropriate?', 'It accommodates the group’s size|It is the cheapest room|It is the only room with a projector|It includes free lunch', 'Soixante participants dépassent les quarante places de Cedar ; Maple en propose quatre-vingts.', 'synthesis'),
 ('How much is the required deposit?', '€130|€80|€274|€650', 'Le dépôt porte sur la location seule : 20 % de 650 € = 130 €.', 'synthesis'),
 ('What service has Tina declined?', 'Lunch|Refreshments|A projector|Room hire', 'La demande précise « no lunch » : le déjeuner est exclu, tandis que les boissons et la salle sont demandées.', 'detail'),
 ('What information does Tina request?', 'Accessibility for wheelchair users|The number of projectors|The lunch menu|The hotel’s checkout time', 'Tina demande confirmation de l’accès en fauteuil roulant.', 'detail'),
 ('What is the total for room hire and refreshments?', '€1,370|€650|€720|€2,090', 'Location 650 € + 60 × 12 € de collations = 1 370 €.', 'synthesis')]),
('An order and an invoice', [
 ('Order · Beacon Design', 'Order 762 · 4 August\nRequested: 12 ergonomic chairs at €180 each, colour charcoal. Delivery address: 14 Mill Road. Please deliver after 10 a.m. on 12 August, when our reception desk opens. Assembly service requested at €15 per chair. Contact: Jules Martin.'),
 ('Invoice · Oakline Furniture', 'Invoice 762-A\n12 ergonomic chairs, charcoal: €2,160\nAssembly service: €180\nDelivery: €40\nTotal due: €2,380\nTerms: payment within 30 days of delivery. Scheduled delivery: 12 August, 8–10 a.m. Please check these details and contact us if any amendment is needed.'),
 ], [
 ('What discrepancy should Jules report?', 'The delivery time|The chair colour|The number of chairs|The assembly charge', 'La commande exige après 10 h ; la facture indique 8–10 h.', 'synthesis'),
 ('How much does assembly cost per chair?', '€15|€12|€40|€180', '180 € divisés par 12 chaises font 15 €, conforme à la commande.', 'synthesis'),
 ('When is payment due?', 'Within thirty days after delivery|Before the order is placed|On 4 August only|At least a week before delivery', 'Les conditions courent à compter de la livraison, pas de la commande.', 'detail'),
 ('Why was a late-morning delivery requested?', 'Reception opens at ten|The road is closed all morning|Assembly takes ten hours|The chairs are made that morning', 'Le courriel explique l’ouverture de l’accueil à 10 h.', 'detail'),
 ('What does “amendment” mean here?', 'Change|Deposit|Complaint fee|Receipt', 'Une amendment est une modification à apporter aux informations.', 'vocabulary')]),
('A training reimbursement', [
 ('Policy · Learning expenses', 'External courses related to an employee’s role may be reimbursed up to €500 per year. Prior written approval is required. Travel expenses are excluded. Submit a receipt and attendance certificate within 30 days of the course. Reimbursement is reduced by any learning allowance already used that year.'),
 ('Email · Approved request', 'To: Sara Khan\nYour request to attend the data visualisation course on 9 October is approved. The course fee is €420. Our records show that you received €150 toward a writing course in February. Please retain your documents and submit your claim promptly.\nHR team'),
 ('Receipt · ClearData Academy', 'Participant: Sara Khan\nCourse: Data visualisation, 9 October\nCourse fee paid: €420\nOptional printed handbook: declined\nCertificate of attendance issued on 9 October.\nTrain ticket purchased separately: €38.'),
 ], [
 ('What is Sara’s remaining annual allowance before this course?', '€350|€500|€420|€150', 'Plafond annuel 500 € moins 150 € déjà utilisés = 350 €.', 'synthesis'),
 ('How much can Sara claim for the course?', '€350|€420|€458|€500', 'Le remboursement est limité au reliquat de 350 €, même si la formation coûte 420 €.', 'synthesis'),
 ('Which expense is excluded?', 'The train ticket|An approved course fee|The earlier writing course|All October courses', 'La politique exclut explicitement les déplacements.', 'detail'),
 ('Which documents are required for the claim?', 'A receipt and an attendance certificate|A passport and a timetable|A handbook and a train ticket|A bank statement only', 'Les deux justificatifs sont mentionnés dans la politique et disponibles selon le reçu.', 'synthesis'),
 ('What can be inferred about the handbook?', 'Sara did not buy it|It cost €38|It was compulsory|HR refused to reimburse it', 'La ligne optional printed handbook: declined indique qu’elle ne l’a pas pris.', 'inference')]),
('A hotel booking change', [
 ('Booking confirmation · Coastview Hotel', 'Guest: Morgan Lee\nStay: 6–9 November, three nights\nRoom: standard, €110 per night\nBreakfast: €14 per person per day, not included\nFree cancellation or changes until 48 hours before arrival. After this deadline, one night is charged for a cancellation. Check-in from 3 p.m.'),
 ('Email · 1 November', 'Hello,\nMy conference now ends a day earlier. Please shorten my stay so I check out on 8 November. I will arrive alone and would like breakfast on both mornings. Can you confirm the revised total?\nMorgan Lee'),
 ('Hotel reply · 2 November', 'Dear Morgan,\nWe have amended your reservation as requested. Your nightly room rate is unchanged, and no modification fee applies. Breakfast has been added for your stay. Please note that the restaurant opens at 6:30 a.m. on weekdays and 7 a.m. at weekends.\nCoastview Reservations'),
 ], [
 ('How many nights is the revised booking?', 'Two|One|Three|Four', 'Arrivée le 6, départ le 8 : deux nuits.', 'synthesis'),
 ('What is the revised total, including breakfast?', '€248|€220|€358|€262', 'Deux nuits × 110 € + deux petits-déjeuners × 14 € = 248 €.', 'synthesis'),
 ('Why is no modification fee charged?', 'The request was made before the deadline|The guest is staying longer|All conference guests are exempt|The room rate has increased', 'La demande du 1 novembre précède de plus de 48 h l’arrivée du 6.', 'synthesis'),
 ('What does the hotel confirm is unchanged?', 'The nightly room price|The checkout date|The number of breakfasts|The length of the conference', 'Your nightly room rate is unchanged confirme le maintien du tarif par nuit.', 'detail'),
 ('What is the purpose of Morgan’s message?', 'To adjust a reservation|To complain about breakfast|To cancel the conference|To ask for a larger room', 'Morgan souhaite raccourcir le séjour et ajouter le petit-déjeuner.', 'intent')]),
('A recruitment schedule', [
 ('Job posting · Operations analyst', 'Required: at least two years of analytical experience and confident spreadsheet skills. Familiarity with SQL is advantageous but not mandatory. Applications close on 7 February. Shortlisted candidates complete a 45-minute online task before a panel interview. The role is based in Bristol with two remote days per week.'),
 ('Email · Interview invitation', 'Dear Casey,\nWe have reviewed your application and would like to invite you to an interview on 19 February at 10 a.m. Please complete the online task by 16 February. You will receive a link separately. Let us know if you require any adjustments to the assessment.\nRecruitment team'),
 ('Email · Casey’s reply', 'Thank you for the invitation. I can attend at the proposed time. I have three years of forecasting experience and use spreadsheets daily, though I am still learning SQL. I have received the task link and will submit my work by the deadline. Could you confirm whether the interview will be online or at your Bristol office?'),
 ], [
 ('Which criterion does Casey clearly meet?', 'The minimum analytical experience|Advanced SQL certification|Five years of management|Daily office attendance', 'Trois ans de prévision dépassent les deux ans d’expérience analytique demandés.', 'synthesis'),
 ('By when must Casey finish the task?', '16 February|7 February|19 February|21 February', 'L’invitation fixe le rendu au 16 février, avant l’entretien du 19.', 'detail'),
 ('Why is Casey’s limited SQL knowledge not automatically disqualifying?', 'SQL is desirable rather than required|The task has been cancelled|Casey will not use a computer|The role requires no analysis', 'L’annonce indique advantageous but not mandatory pour SQL.', 'synthesis'),
 ('What remains unclear to Casey?', 'The interview format|The task deadline|The proposed time|The company’s city', 'Casey demande si l’entretien sera en ligne ou au bureau.', 'inference'),
 ('What has Casey already received?', 'The task link|A job offer|Travel reimbursement|A revised contract', 'Le courriel de réponse confirme la réception du lien.', 'detail')]),
]
for i, (title, docs, items) in enumerate(MULTI):
    add(f'p7-m{i+1:02}', 7, title, [q(*x, level='C1') for x in items], documents=[{'title': t, 'body': b} for t,b in docs], passage_type='double' if len(docs)==2 else 'triple')

FLASHCARDS = [
 ('reimburse', 'rembourser', 'The company will reimburse your travel expenses.', 'vocabulary'),
 ('outstanding', 'en attente / impayé', 'Please settle the outstanding balance by Friday.', 'vocabulary'),
 ('complimentary', 'gratuit / offert', 'Guests receive complimentary breakfast.', 'vocabulary'),
 ('provided that', 'à condition que', 'We can deliver tomorrow provided that you order today.', 'connectors'),
 ('regardless of', 'indépendamment de', 'The policy applies regardless of seniority.', 'connectors'),
 ('subject to', 'soumis à / susceptible de', 'Prices are subject to change.', 'vocabulary'),
 ('prior to', 'avant', 'Approval is required prior to enrolment.', 'prepositions'),
 ('upon receipt', 'dès réception', 'Payment is due upon receipt of the invoice.', 'prepositions'),
 ('to waive a fee', 'renoncer à des frais', 'The hotel agreed to waive the cancellation fee.', 'vocabulary'),
 ('a quotation', 'un devis', 'Could you send us a detailed quotation?', 'vocabulary'),
 ('to meet a deadline', 'respecter une échéance', 'The team worked together to meet the deadline.', 'vocabulary'),
 ('to put off', 'reporter', 'We had to put off the launch until June.', 'vocabulary'),
 ('a drawback', 'un inconvénient', 'The only drawback is the limited parking.', 'vocabulary'),
 ('a prerequisite', 'une condition préalable', 'Written approval is a prerequisite for reimbursement.', 'vocabulary'),
 ('to account for', 'expliquer / représenter', 'Online orders account for half of our sales.', 'vocabulary'),
 ('whereas', 'tandis que (contraste)', 'The first plan is cheap, whereas the second is more flexible.', 'connectors'),
 ('despite + noun', 'malgré + nom ou gérondif', 'Despite the delay, the event started on time.', 'connectors'),
 ('although + clause', 'bien que + proposition', 'Although it was raining, the delivery arrived.', 'connectors'),
 ('since + starting point', 'depuis un point de départ', 'She has worked here since 2021.', 'tenses'),
 ('for + duration', 'pendant / depuis une durée', 'She has worked here for five years.', 'tenses'),
 ('to be eligible for', 'remplir les conditions pour', 'Permanent employees are eligible for this benefit.', 'prepositions'),
 ('to comply with', 'se conformer à', 'All contractors must comply with safety rules.', 'prepositions'),
 ('to be liable for', 'être responsable de', 'The supplier is liable for damage during transport.', 'prepositions'),
 ('to run out of', 'ne plus avoir de', 'We have run out of printer paper.', 'vocabulary'),
 ('tentative', 'provisoire', 'The tentative schedule will be confirmed tomorrow.', 'vocabulary'),
 ('to expedite', 'accélérer le traitement de', 'We will expedite your replacement order.', 'vocabulary'),
 ('contingent on', 'subordonné à', 'The offer is contingent on final approval.', 'prepositions'),
 ('notwithstanding', 'nonobstant / malgré', 'The contract remains valid notwithstanding the delay.', 'connectors'),
 ('to offset', 'compenser', 'The savings should offset the initial cost.', 'vocabulary'),
 ('to stem from', 'provenir de', 'The delay stems from a shortage of components.', 'vocabulary'),
]

LESSONS = [
 {'id': 'word-forms', 'title': 'Reconnaître la bonne famille de mots', 'subtitle': 'Partie 5 · Le réflexe qui fait gagner du temps', 'minutes': 8, 'level': 'B1 → B2', 'sections': [
 ('La position avant le sens', 'Commence par identifier la fonction manquante. Après un déterminant (a, the, our), cherche le noyau nominal. Un adjectif peut se placer entre les deux. Un adverbe modifie un verbe, un adjectif ou un autre adverbe.'),
 ('Observe la structure', 'The team responded promptly. → promptly modifie responded.\nA prompt response is required. → prompt qualifie response.\nWe appreciate your cooperation. → cooperation est un nom.'),
 ('Le piège de -ly', 'Tous les mots en -ly ne sont pas des adverbes : friendly, costly et likely peuvent être adjectifs. Ne choisis jamais sur la seule terminaison. Hard et fast peuvent être des adverbes sans -ly ; hardly signifie presque pas.'),
 ('Méthode en trois gestes', '1. Regarde les mots qui encadrent le blanc.\n2. Identifie nom, verbe, adjectif ou adverbe.\n3. Relis la phrase entière pour vérifier le sens.\nEn entraînement, vise d’abord la justesse, puis environ 25 à 35 secondes par phrase courte.') ]},
 {'id': 'tenses', 'title': 'Situer les actions dans le temps', 'subtitle': 'Passé simple, present perfect et antériorité', 'minutes': 10, 'level': 'B1 → C1', 'sections': [
 ('Un passé terminé', 'Un repère clos comme yesterday, last week ou in 2020 appelle généralement le prétérit pour une action accomplie : The board approved the plan yesterday.'),
 ('Un lien avec maintenant', 'Le present perfect relie le passé au présent : We have received three applications so far. Avec since ou for, il peut exprimer une situation qui continue : She has worked here since May.'),
 ('Une action avant une autre', 'Past perfect : The team had finished before the client arrived.\nFuture perfect : By Friday, we will have completed the audit.\nNe choisis pas un temps composé uniquement parce que la phrase semble difficile : cherche son repère.'),
 ('Passif et conditionnel', 'The invoices had been filed : les factures subissent l’action.\nIf we had known, we would have acted : condition irréelle passée.\nHad we known, we would have acted est une inversion formelle équivalente.') ]},
 {'id': 'connectors', 'title': 'Choisir le bon lien logique', 'subtitle': 'Concession, cause, but et condition', 'minutes': 7, 'level': 'B1 → C1', 'sections': [
 ('Deux contrôles complémentaires', 'Un connecteur doit convenir au sens ET à la structure. Although + sujet/verbe ; despite + nom ou gérondif. Because + proposition ; because of + nom.'),
 ('But ou conséquence ?', 'So that + proposition exprime le but : We left early so that we could arrive on time. Therefore exprime une conséquence et nécessite une ponctuation adaptée. In order to est suivi d’une base verbale.'),
 ('Condition et contraste', 'Provided that et as long as posent une condition. Unless signifie except if, pas simplement if. Whereas oppose deux faits. Nevertheless reprend un contraste avec la phrase précédente.'),
 ('Niveau avancé', 'No sooner…than ; hardly…when.\nShould you need help = If you should need help.\nPlausible though it sounds = Although it sounds plausible.\nCes structures de précision sont proposées seulement après consolidation des bases.') ]},
 {'id': 'prepositions', 'title': 'Les associations à automatiser', 'subtitle': 'Apprendre des groupes de mots complets', 'minutes': 6, 'level': 'B1 → B2', 'sections': [
 ('Apprends la collocation', 'Responsible for ; compatible with ; depend on ; eligible for ; entitled to ; comply with. Mémorise chaque association dans une phrase, pas comme deux mots isolés.'),
 ('To n’est pas toujours un infinitif', 'Look forward to meeting you ; committed to reducing waste. Ici to est une préposition, donc le verbe suivant prend -ing. Compare : expected to reduce waste, où to introduit l’infinitif.'),
 ('Dates et délais', 'By Friday : au plus tard vendredi. Until Friday : jusqu’à vendredi. Within three days : avant l’expiration de trois jours. On Monday, in July, at noon.'),
 ('Révision active', 'Cache la préposition et prononce la phrase entière. Reviens sur les associations difficiles demain, puis dans quelques jours. Une réponse immédiatement reconnue n’est pas encore une récupération autonome.') ]},
 {'id': 'agreement', 'title': 'Accords, relatives et inversions', 'subtitle': 'Trouver le vrai sujet', 'minutes': 9, 'level': 'B2 → C1', 'sections': [
 ('Le noyau commande l’accord', 'Each of the proposals includes… : each est singulier. The list of items is… : list est le noyau, même si items est proche du verbe. Écarte mentalement les compléments pour retrouver le sujet.'),
 ('Relatives', 'Who désigne une personne sujet ; which peut reprendre une chose ou toute une proposition ; whose marque la possession. Whoever wishes to apply : whoever est sujet de wishes, même après une préposition dans la proposition principale.'),
 ('Formes verbales attendues', 'Recommend doing ; encourage someone to do ; insist that something be done. Apprends la structure complète. La construction passive peut modifier la forme qui suit.'),
 ('Inversion de niveau avancé', 'Not only did she meet the deadline…\nSeldom have we received…\nSo substantial were the savings…\nRepère le déclencheur en tête de proposition et rétablis l’ordre auxiliaire-sujet-verbe.') ]},
 {'id': 'vocabulary', 'title': 'Le vocabulaire professionnel en contexte', 'subtitle': 'Achats, projets, recrutement et services', 'minutes': 8, 'level': 'B1 → C1', 'sections': [
 ('Achats et facturation', 'Quotation = devis ; invoice = facture ; receipt = reçu ; outstanding balance = solde restant dû ; refund = remboursement d’un achat ; reimburse = rembourser une dépense engagée.'),
 ('Projets et recrutement', 'Meet a deadline, postpone a launch, submit a proposal, shortlist a candidate, prior approval. Apprends le verbe avec son complément.'),
 ('Faux amis et formes proches', 'Complimentary = offert ; complementary = complémentaire.\nEventually = finalement ; possibly = éventuellement.\nActual = réel ; current = actuel.\nAssistance = aide ; attendance = présence.'),
 ('De la reconnaissance à l’usage', 'Avant de retourner une carte, formule une traduction ou une phrase. Si tu reconnais seulement le mot après avoir vu le verso, choisis À revoir. La répétition espacée dépend de cette honnêteté.') ]},
 {'id': 'detail', 'title': 'Lire vite sans perdre les détails', 'subtitle': 'Partie 7 · Questions, repères, preuve', 'minutes': 9, 'level': 'B2', 'sections': [
 ('Une lecture orientée', 'Identifie le type de document et son but. Lis la question, puis cherche un indice correspondant : personne, date, condition, montant. Lis aussi la phrase précédente et la suivante pour éviter une correspondance de mots trompeuse.'),
 ('Justifie avant de valider', 'Repère le passage qui prouve la réponse. Un mot identique à la question peut apparaître dans un distracteur. Les bonnes réponses utilisent souvent une reformulation.'),
 ('Budget de temps', 'Point de départ ajustable pour les 75 minutes : environ 10 minutes en partie 5, 8 en partie 6, 57 en partie 7. Ce n’est pas une règle officielle. Tes temps et tes erreurs doivent modifier cette stratégie.'),
 ('Ne t’enlise pas', 'Si deux lectures ciblées ne suffisent pas, sélectionne la réponse la plus étayée et marque la question. Garde une marge pour les documents multiples. Les mauvaises réponses ne retirent pas de points au test officiel.') ]},
 {'id': 'inference', 'title': 'Déduire sans inventer', 'subtitle': 'Faire le plus petit raisonnement nécessaire', 'minutes': 7, 'level': 'B2 → C1', 'sections': [
 ('Une inférence reste prouvable', 'Un restaurant peut accueillir six personnes à une table : un groupe de huit doit chercher une autre solution. En revanche, on ne peut pas conclure que le restaurant est complet.'),
 ('Connecte deux indices', '“I have a meeting at two” + “The receptionist will be here” implique que la réception accueillera le technicien. N’ajoute pas de motif personnel non exprimé.'),
 ('Attention aux limites', 'May, might et where possible signalent une possibilité ; must et required une obligation. Ne transforme pas une possibilité en garantie. Not necessarily ne signifie pas jamais.'),
 ('Auto-explication', 'Après une erreur, écris mentalement : “J’ai choisi X parce que… mais le texte établit seulement…” Le carnet d’erreurs te redonnera ces items après un délai.') ]},
 {'id': 'intent', 'title': 'Comprendre ce que la personne veut dire', 'subtitle': 'Parties 2, 3 et 4 · Réponses indirectes', 'minutes': 8, 'level': 'B2 → C1', 'sections': [
 ('Forme et fonction', 'Why don’t we…? est une suggestion, pas une demande de cause. Could you…? est souvent une demande d’action. Would you mind…? demande une coopération.'),
 ('Réponse implicite', '“Can the repair wait?” — “We need the machine today.” signifie probablement non. “Has it been approved?” — “We are still waiting.” signifie pas encore. Écoute la fonction de la réponse.'),
 ('Pièges sonores', 'Train/training, fair/fare, order au sens de commande ou d’ordre. La répétition d’un son ne prouve pas une réponse. Retrouve le sens global avant de sélectionner.'),
 ('Accents et écoute', 'Alterne les voix proposées. Première écoute sans transcription, réponse, puis correction et transcription. Réécoute le passage mal compris. Les voix synthétiques servent l’entraînement ; complète par les ressources audio officielles liées dans l’application.') ]},
 {'id': 'synthesis', 'title': 'Croiser deux ou trois documents', 'subtitle': 'Partie 7 · Relier les informations utiles', 'minutes': 10, 'level': 'B2 → C1', 'sections': [
 ('Donne un rôle à chaque document', 'Offre = règles ; commande = besoin ; réponse = décision finale. Repère qui écrit et à quelle date. Une modification ultérieure peut remplacer une information initiale.'),
 ('Une petite table mentale', 'Pour un remboursement : plafond, montant déjà utilisé, coût admissible. Pour une réservation : dates, tarif unitaire, extras, conditions. Ne mélange pas acompte, prix total et frais annexes.'),
 ('Calculs simples, lecture précise', 'Un acompte de 20 % sur la location ne s’applique pas forcément au traiteur. “Per person per day” multiplie par personnes ET jours. Lis les unités avant de calculer.'),
 ('Choix de phrase et cohérence', 'Pour une insertion, vérifie les pronoms, les temps, les connecteurs et l’enchaînement thématique. Une phrase grammaticalement correcte peut être incohérente dans le document.') ]},
 {'id': 'visual', 'title': 'Associer l’audio au support visuel', 'subtitle': 'Photographies, tableaux et graphiques', 'minutes': 6, 'level': 'B1 → B2', 'sections': [
 ('Photographies', 'Observe personnes, objets et positions. Distingue l’action visible d’un état : a door is open n’implique pas someone is opening it. N’invente pas une intention.'),
 ('Tableaux et graphiques', 'Lis les titres et les unités avant l’écoute. L’audio peut nommer un mois tandis que les réponses donnent des montants. Il faut relier ces deux représentations.'),
 ('Changements et corrections', 'Un locuteur peut donner un premier horaire puis se corriger. Retenir le dernier horaire valide compte plus que reconnaître le premier nombre.'),
 ('Pratique', 'Avant d’écouter, anticipe seulement le type d’information nécessaire. Après correction, identifie si l’erreur vient de l’audio, de la lecture du tableau ou du lien entre les deux.') ]},
]

def bank_summary():
    return {str(p): sum(len(g['questions']) for g in GROUPS if g['part'] == p) for p in PARTS}

for _group in GROUPS:
    _group['exam_set'] = 1
    _group['variant'] = False

from server.expansion import expand
expand(add, q)

from server.vocabulary import cards as vocabulary_cards
_known_words = {x[0] for x in FLASHCARDS}
FLASHCARDS.extend(x for x in vocabulary_cards() if x[0] not in _known_words)
