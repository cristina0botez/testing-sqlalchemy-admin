engine = create_engine(
    'sqlite:///example.db',
    connect_args={'check_same_thread': False},
)
Session = sessionmaker(engine)
