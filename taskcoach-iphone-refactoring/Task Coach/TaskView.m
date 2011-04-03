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

- (IBAction)onDone:(id)sender
{
    doneAction(self);
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation
{
    return YES;
}

@end
