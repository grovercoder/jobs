#!.venv/bin/python3

import argparse

from jobs.routines import check_site, clear_job_queue, load_big4, load_sites, report_cli, reset_database, scan_queued_jobs, site_list, seed_db, compare_file, purge_old_jobs, rescan_job_keywords, serve

def str_to_bool(value):
    value = value.lower()
    if value in ("false", "no", "0", "off"):
        return False
    else:
        return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Control script for the jobs application")
    parser.add_argument("--cq", "--clear-queue", action = "store_true", help="Clear the job_queues")
    parser.add_argument("--big4", action="store_true", help="Load jobs from the big 4 job boards (Indeed, LinkedIn, Glassdoor, Ziprecruiter)")
    parser.add_argument("--sites", action="store_true", help="Load job URLs from the listing sites")
    parser.add_argument("--full", action="store_true", help="Load the big4, scan sites, collect job details")
    parser.add_argument("--load", action="store_true", help="Load the big4, and scan sites for job links")
    parser.add_argument("--collect", action="store_true", help="Load job details from queued job urls")
    parser.add_argument("--status", action="store_true", help="Report table sizes")
    parser.add_argument("--reset", action="store_true", help="Delete the database and re-initialize it.")
    parser.add_argument("--list-sites", action="store_true", help="List the names of the listing sites")
    parser.add_argument("--scan", type=str, required=False, help="Scan the specified site for new job urls to add to the queue.")
    parser.add_argument("--random", required=False, default=True, type=str_to_bool, help="True = single random location/search-term. False = all combinations. (default: True)")
    parser.add_argument("--clean", action="store_true", help="clean up the database")
    parser.add_argument("--seed", action="store_true", help="apply seed data to database")
    parser.add_argument("--compare", type=str, required=False, help="Perform keyword matching for specified file")
    parser.add_argument("--context", type=str, required=False, default="IT", help="What keyword context to use when comparing")
    parser.add_argument("--rescan-keywords", action="store_true", help="Extract weighted keywords for the job descriptions")
    parser.add_argument("--serve", action="store_true", help="Start the web server")
    
    
    args = parser.parse_args()

    # print(args)
    # quit()

    if args.cq:
        response = input("Clear the queue table? [y/N] ").strip().lower()
        confirmed = response in ['y', 'yes']
        if confirmed:
            clear_job_queue()
        else:
            print('no task selected')
        quit()

    if args.reset:
        print("WARNING:  This will loose all current data!!")
        response = input("Erase the database and reinitialize? [y/N] ").strip().lower()
        confirmed = response in ['y', 'yes']
        if confirmed:
            reset_database()
        else:
            print('no task selected')

    if args.seed:
        print("WARNING: Applying seed data to an existing database may cause duplicate records")
        response = input("Apply seed data? [y/N] ").strip().lower()
        confirmed = response in ['y', 'yes']
        if confirmed:
            seed_db()
        else:
            print('no task selected')

    if args.big4:
        load_big4(randomize=args.random)

    if args.sites:
        load_sites(randomize=args.random)

    if args.collect:
        scan_queued_jobs()

    if args.load:
        load_big4(randomize=args.random)
        load_sites(randomize=args.random)

    if args.full:
        load_big4(randomize=args.random)
        load_sites(randomize=args.random)
        scan_queued_jobs()

    if args.status:
        report_cli()

    if args.scan:
        check_site(args.scan)

    if args.list_sites:
        site_list()

    if args.compare:
        compare_file(args.compare, context=args.context)

    if args.clean:
        purge_old_jobs()

    if args.rescan_keywords:
        rescan_job_keywords()

    if args.serve:
        serve()
