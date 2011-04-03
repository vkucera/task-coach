//
//  TasklistView.m
//  Task Coach
//
//  Created by Jérôme Laheurte on 13/03/11.
//  Copyright 2011 __MyCompanyName__. All rights reserved.
//

#import "Task_CoachAppDelegate.h"
#import "TasklistView.h"
#import "Configuration.h"
#import "AlertPrompt.h"
#import "CDList.h"
#import "i18n.h"

@implementation TasklistView

- (id)initWithAction:(void (^)(UIViewController *))action
{
    if ((self = [super initWithNibName:@"TasklistView" bundle:[NSBundle mainBundle]]))
    {
        doneAction = Block_copy(action);
    }

    return self;
}

- (void)dealloc
{
    Block_release(doneAction);

    [listsCtrl release];
    [toolbar release];
    [super dealloc];
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation
{
    return YES;
}

- (IBAction)onSave:(id)sender
{
    doneAction(self);
}

- (IBAction)onAdd:(id)sender
{
    AlertPrompt *alert = [[AlertPrompt alloc] initWithTitle:_("New list name:") message:_("\n\n") cancelAction:^(void) {
    } confirmAction:^(NSString *name) {
        CDList *list = [NSEntityDescription insertNewObjectForEntityForName:@"CDList" inManagedObjectContext:getManagedObjectContext()];
        list.name = name;
        
        NSError *error;
        if (![getManagedObjectContext() save:&error])
        {
            NSLog(@"Could not save: %@", [error localizedDescription]);
        }

        [Configuration instance].currentList = list;
        [[Configuration instance] save];

        doneAction(self);
    } secure:NO];
    [alert show];
    [alert release];
}

#pragma mark - View lifecycle

- (void)viewDidLoad
{
    [super viewDidLoad];

    NSMutableArray *items = [NSMutableArray arrayWithArray:toolbar.items];
    [items addObject:listsCtrl.editButtonItem];
    [toolbar setItems:items animated:NO];

    listsCtrl.parent = self;
}

- (void)viewDidUnload
{
    [listsCtrl release];
    listsCtrl = nil;
    [toolbar release];
    toolbar = nil;
    [super viewDidUnload];
}

@end
