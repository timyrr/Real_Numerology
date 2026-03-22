CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_users_id ON users (id);
CREATE INDEX IF NOT EXISTS ix_users_username ON users (username);

CREATE TABLE IF NOT EXISTS user_sessions (
    id SERIAL PRIMARY KEY,
    token VARCHAR(128) NOT NULL UNIQUE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_user_sessions_id ON user_sessions (id);
CREATE INDEX IF NOT EXISTS ix_user_sessions_token ON user_sessions (token);
CREATE INDEX IF NOT EXISTS ix_user_sessions_user_id ON user_sessions (user_id);

CREATE TABLE IF NOT EXISTS posts (
    id SERIAL PRIMARY KEY,
    title VARCHAR(150) NOT NULL,
    content TEXT NOT NULL,
    image_url VARCHAR(255) NOT NULL DEFAULT '/static/post-images/default.svg',
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_posts_id ON posts (id);
CREATE INDEX IF NOT EXISTS ix_posts_user_id ON posts (user_id);
CREATE INDEX IF NOT EXISTS ix_posts_title ON posts (title);
CREATE INDEX IF NOT EXISTS ix_posts_created_at ON posts (created_at);

CREATE TABLE IF NOT EXISTS galaxy_numbers (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    number INTEGER NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_galaxy_numbers_id ON galaxy_numbers (id);
CREATE INDEX IF NOT EXISTS ix_galaxy_numbers_user_id ON galaxy_numbers (user_id);
CREATE INDEX IF NOT EXISTS ix_galaxy_numbers_created_at ON galaxy_numbers (created_at);

INSERT INTO users (id, username, password_hash)
VALUES
    (
        1,
        'number_fan',
        'pbkdf2_sha256$600000$8005ca5d8e1ffa63f95747b20aedf14e$nIzZDY1uKqC_47r2A_TMLbe4_Fe5Z1h5HoYPh2tGq7A' --bhEUSrhyzzbEApngXDRLBHeZ8bZXzZ
    ),
    (
        2,
        'leet_writer',
        'pbkdf2_sha256$600000$4c9176be293f318a05129918ca01f45c$zEeM9DvBop-saMk1UehPMMzwmmu-pzR_w7nmk0zyxXc' --m557GBazL6f3ka2gtdV386Un2Y3X7p
    )
ON CONFLICT (id) DO NOTHING;

INSERT INTO posts (id, title, content, image_url, user_id)
VALUES
    (
        1,
        'Почему число 42 стало культовым?',
        'Согласно нумерологии, кармическое число 42 означает выносливость, высокую мотивацию в работе, постоянное стремление к балансу и гармонии. Цифра шесть, которая получается при сложении четверки и двойки, символизирует миролюбие и доброту.
        Судьба, отмеченная числом 42, не будет бурной и полной страстей. Этот знак по сути своей – символ простой, спокойной и размеренной жизни. Авантюры и риски не присущи человеку этого номера. Но о его характере стоит поговорить подробнее, потому что у него есть неочевидные особенности.
        Человек с числом 42
        Люди числа 42 имеют гармоничный характер. Однако эти цифры могут проявляться как положительно, так и негативно. Многое зависит от самого человека. Например, в каких условиях он воспитывался, кем работает, как реагирует на жизненные повороты и какой выбор делает в сложных ситуациях. Разберем плюсы и минусы характера тех, кто связан с числом 42 по дате рождения.',
        '/static/post-images/42_demo.png',
        1
    ),
    (
        2,
        '67 В С Ё - жесткий разбор числа 67!',
        'Число 67 - это число, которое придает людям особую харизму и таинственную красоту, вызывая восхищение у тех, кто его наблюдает. Комбинирование чисел 6 и 7 символизирует путь от жизни к смерти и далее, пропитывая этот переход трансцендентностью и духовностью. Цифра 6 олицетворяет красоту и совершенство, в то время как число 7 дарит загадочность. Вместе они создают числовую сумму, полную таинственности.
         Известное произведение искусства - "Мона Лиза" Леонардо да Винчи, испускает энергию, пропитанную числом 67. Это произведение идеально сочетает в себе красоту и гармонию, как технически, так и пропорционально. Золотое сечение пронизывает его каждую деталь. Одновременно с этим, картина "Мона Лиза" кажется загадочной и своего рода между мирами. Ее загадочная улыбка и спокойный взгляд оставляют нас с вопросами: она счастлива или грустна? Это не столь очевидно, как можно подумать. Существует множество теорий и мнений на этот счет, но мы не знаем правды.
         В случае дисбаланса число 67 может создавать ощущение высокомерности, затруднения, нелепости, туманности, застенчивости, одиночества и непонимания. Оно может быть настолько насыщенным внутри, что не может найти выход и часто перекрывает разговоры и сбивает с толку. Многие люди с дисгармоничным числом 67 страдают от граничных тенденций.
         Сбалансированное число 67 олицетворяет любовь, тайну, очарование, эстетическое чувство и глубокую духовность.',
        '/static/post-images/67.webp',
        1
    ),
    (
        3,
        '52 и Питерское влияние',
        'Число 52 представляет собой комбинацию энергий и вибраций чисел 5 и 2. Понимание значений этих отдельных чисел может помочь нам лучше понять, что символизирует число 52 в нумерологии.
         Число 2 часто называют числом баланса и гармонии. Он ассоциируется с партнерством, сотрудничеством, дипломатией и приспособляемостью. В нумерологии число 2 также связано с интуицией, чувствительностью и самоотверженностью. Когда число 2 появляется в нумерологической диаграмме, это говорит о том, что человек обладает высокой интуицией и обладает отличными коммуникативными навыками. Они имеют естественную способность общаться с людьми и могут легко заводить друзей. Они также прекрасные слушатели, и к ним часто обращаются за мудрым советом.
         Когда объединяем энергии чисел 5 и 2, получаем число 52. В нумерологии число 52 ассоциируется с переменами, трансформацией и новыми возможностями. Люди, которые часто видят число 52 в своих жизнь может переживать период значительных изменений или потрясений. Их поощряют использовать новые возможности и отказываться от старых привычек и стереотипов, которые им больше не служат. Число 52 является напоминанием о том, что перемены могут быть позитивной силой в нашей жизни и что мы должны принимать их с открытым разумом и сердцем.',
        '/static/post-images/52.webp',
        1
    ),
    (
        4,
        '1337 и leet-c4l7ur3',
        '4ng3l numb3r 1337 d3r1v3z 1tz m34n1ng fr0m th3 c0mb1n4t10n 0f 1, 3, 4nd 7. Th3 numb3r 0n3 r3z0n4t3z w1th n3w b3g1nn1ngz, t4k1ng 1n1t14t1v3, 4nd str1v1ng t0w4rdz y0ur g04lz. Th3 numb3r 3 1z 4 symb0l 0f cr34t1v1ty, m4n1f3zt1ng y0ur d3z1r3z, 4nd z3lf-3xpr3zz10n. 0n th3 0th3r h4nd, th3 numb3r 7 r3l4t3z t0 zp1r1tu4l d3v3l0pm3nt, 1nn3r w1zd0m, 4nd 3nl1ght3nm3nt. Th3r3f0r3, 4ng3l Numb3r 1337 1z 4 m3zz4g3 fr0m th3 un1v3rz3 t0 st4y p0z1t1v3 4z y0u 4ppr04ch n3w b3g1nn1ngz z1nc3 th3y br1ng f0rth m4n1f3zt4t10n 0pp0rtun1t13z. Y0ur cr34t1v3 sk1llz 4nd z3lf-3xpr3zz10n w1ll 3n4bl3 y0u t0 thr1v3 4nd succ33d 1n y0ur 3nd34v0rz 1f y0u r3m41n f0cuz3d 4nd d3t3rm1n3d. W1th zp1r1tu4l d3v3l0pm3nt 4nd 1nn3r w1zd0m, y0u c4n 4ch13v3 3v3ryth1ng y0u w4nt 1n l1f3.',
        '/static/post-images/1337.webp',
        2
    ),
    (
        5,
        'Магические числа Вселенной и их связь с флагами',
        'Говорят, и мы на своем опыте проверили, что Вселенная посылает нам разные сигналы через повседневные числа, которые мы видим на каждом шагу.
         Но наш сайт научился напрямую получать данные числа, и скоро каждый пользователь сможет запросить свое число у Вселенной и наконец-то разобраться в себе, своих отношения, работе и т.д.
         Разные числа могут означать разное, но благодаря нашим источникам, таким как: карты таро, гадания на кофейной гуще, доска Уиджи, стало известно, что если вам Вселенная посылает число, равное сумме чисел 51966 и 47806, которые в 16 виде выглядят как CAFE и BABE, то вам сказочно повезло и в скором времени вы будете замечать флаги, которые Вселенная также отправляет только вам.',
        '/static/post-images/galaxy_flag.png',
        2
    )
ON CONFLICT (id) DO NOTHING;

INSERT INTO galaxy_numbers (id, user_id, number)
VALUES
    (
        1,
        1,
        425267
    ),
    (
        2,
        2,
        31337
    )
ON CONFLICT (id) DO NOTHING;

SELECT setval(pg_get_serial_sequence('users', 'id'), COALESCE((SELECT MAX(id) FROM users), 1), true);
SELECT setval(pg_get_serial_sequence('user_sessions', 'id'), COALESCE((SELECT MAX(id) FROM user_sessions), 1), true);
SELECT setval(pg_get_serial_sequence('posts', 'id'), COALESCE((SELECT MAX(id) FROM posts), 1), true);
SELECT setval(pg_get_serial_sequence('galaxy_numbers', 'id'),COALESCE((SELECT MAX(id) FROM galaxy_numbers), 1),true);