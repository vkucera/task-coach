//
//  TaskView.m
//  Task Coach
//
//  Created by Jérôme Laheurte on 03/04/11.
//  Copyright 2011 __MyCompanyName__. All rights reserved.
//

#import "TaskView.h"
#import "Task_CoachAppDelegate.h"
#import "CDDomainObject+Addons.h"
#import "CDTask+Addons.h"
#import "Configuration.h"
#import "SmartActionSheet.h"
#import "NSDateUtils.h"
#import "i18n.h"

@implementation TaskView

- (id)initWithAction:(void (^)(UIViewController *))action
{
    if ((self = [super initWithNibName:@"TaskView" bundle:[NSBundle mainBundle]]))
    {
        doneAction = Block_copy(action);

        // Update date status for all objects
        NSFetchRequest *request = [[NSFetchRequest alloc] init];
        [request setEntity:[NSEntityDescription entityForName:@"CDTask" inManagedObjectContext:getManagedObjectContext()]];
        [request setPredicate:[NSPredicate predicateWithFormat:@"status != %d AND list=%@", STATUS_DELETED, [Configuration instance].currentList]];

        NSError *error;
        NSArray *tasks = [getManagedObjectContext() executeFetchRequest:request error:&error];
        if (tasks)
        {
            for (CDTask *task in tasks)
                [task computeDateStatus];
            
            if (![getManagedObjectContext() save:&error])
            {
                UIAlertView *alert = [[UIAlertView alloc] initWithTitle:@"Error" message:[NSString stringWithFormat:@"Could not save tasks: %@", [error localizedDescription]] delegate:self cancelButtonTitle:@"OK" otherButtonTitles:nil];
                [alert show];
                [alert release];
                NSLog(@"Error: %@", error);
            }
        }
        else
        {
            UIAlertView *alert = [[UIAlertView alloc] initWithTitle:@"Error" message:[NSString stringWithFormat:@"Could not load tasks: %@", [error localizedDescription]] delegate:self cancelButtonTitle:@"OK" otherButtonTitles:nil];
            [alert show];
            [alert release];
            NSLog(@"Error: %@", error);
        }
        
        [request release];
    }

    return self;
}

- (void)dealloc
{
    Block_release(doneAction);
    
    [taskTableCtrl release];

    [super dealloc];
}

- (void)viewDidAppear:(BOOL)animated
{
    refreshStatusTimer = [[NSTimer scheduledTimerWithTimeInterval:[[NSDateUtils dateRoundedTo:15] timeIntervalSinceNow] target:self selector:@selector(onRefreshStatus:) userInfo:nil repeats:YES] retain];

    [super viewDidAppear:animated];
}

- (void)viewWillDisappear:(BOOL)animated
{
    if (refreshStatusTimer)
    {
        [refreshStatusTimer invalidate];
        [refreshStatusTimer release];
        refreshStatusTimer = nil;
    }

    [super viewWillDisappear:animated];
}

- (void)onRefreshStatus:(NSTimer *)timer
{
    NSFetchRequest *req = [[NSFetchRequest alloc] init];
    [req setEntity:[NSEntityDescription entityForName:@"CDTask" inManagedObjectContext:getManagedObjectContext()]];
    [req setPredicate:[NSPredicate predicateWithFormat:@"status != %d AND list=%@", STATUS_DELETED, [Configuration instance].currentList]];
    NSError *error;
    NSArray *tasks = [getManagedObjectContext() executeFetchRequest:req error:&error];
    [req release];

    if (tasks)
    {
        for (CDTask *task in tasks)
        {
            [task computeDateStatus];
        }

        if (![getManagedObjectContext() save:&error])
        {
            NSLog(@"Could not save after refreshing: %@", [error localizedDescription]);
        }
    }
    else
    {
        NSLog(@"Unable to refresh: %@", [error localizedDescription]);
    }

    [timer setFireDate:[NSDateUtils dateRoundedTo:15]];
}

- (IBAction)onDone:(id)sender
{
    doneAction(self);
}

- (void)toggleGrouping:(NSInteger)grouping
{
    if ([Configuration instance].grouping == grouping)
    {
        [Configuration instance].revertGrouping = ![Configuration instance].revertGrouping;
    }
    else
    {
        [Configuration instance].grouping = grouping;
        [Configuration instance].revertGrouping = NO;
    }

    [[Configuration instance] save];
    [taskTableCtrl reload];
    [taskTableCtrl.tableView reloadData];
}

- (IBAction)onSelectGrouping:(id)sender
{
    SmartActionSheet *sheet = [[SmartActionSheet alloc] initWithTitle:_("Group by") cancelButtonTitle:_("Cancel") cancelAction:^(void) {
    }];

    [sheet addAction:^(void) {
        [self toggleGrouping:GROUPING_STATUS];
    } withTitle:_("Status")];
    
    [sheet addAction:^(void) {
        [self toggleGrouping:GROUPING_PRIORITY];
    } withTitle:_("Priority")];
    
    [sheet addAction:^(void) {
        [self toggleGrouping:GROUPING_START];
    } withTitle:_("Start date")];
    
    [sheet addAction:^(void) {
        [self toggleGrouping:GROUPING_DUE];
    } withTitle:_("Due date")];

    [sheet showInView:self.view];
    [sheet release];
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation
{
    return YES;
}

@end
