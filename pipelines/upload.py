from htag_data_pipeline.outbound.localities import push_localities_to_supabase


def upload_localities_pipeline(data_dir="data", run_date=None, batch_size=1000):
    """Upload clean locality CSV data into Supabase."""
    return push_localities_to_supabase(
        data_dir=data_dir,
        run_date=run_date,
        batch_size=batch_size,
    )


if __name__ == "__main__":
    upload_localities_pipeline()
