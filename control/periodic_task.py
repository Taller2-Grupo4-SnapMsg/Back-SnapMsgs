
from control.common_setup import *
from repository.queries.queries_trending_topics import *


def perform_periodic_task():
    print("Realizando tarea periódica...")

# TODO: si uso web socket esto no va a ser programado, va a ser ante uno nuevo
def report_trending_topics(amount: int = 10, offset: int = 0):
    """
    """
    print("Reporting trending topics...")

    trending_topics = get_trending_topics(amount, offset)
    
    ### TODO: asegurate de que sea una lista
    all_user_emails = get_all_user_emails()

    notificacion_request = NotificationRequest(
        user_emails_that_receive=all_user_emails,
        title="Trending Topics",
        body=f"Popular topics are: {', '.join(trending_topics)}",
        data={"trending_topics": trending_topics},
    )
    #TODO: obtener tokens
    
    send_push_notifications(tokens_db, notificacion_request)

def perform_cleanup(session):
    print("çLimpiando palabras...")
    cleanup_trending_topics(session)

