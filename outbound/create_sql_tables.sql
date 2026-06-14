-- statement to create localities table in investit group
create table If Not exists investitgroup.localities (
    loc_pid text primary key,
    locality text not null,
    postcode text,
    state_name text,
    suburb_key text,
    lga_pid_ref text
);
