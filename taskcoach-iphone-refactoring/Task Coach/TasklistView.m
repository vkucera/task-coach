//
//  TasklistView.m
//  Task Coach
//
//  Created by Jérôme Laheurte on 13/03/11.
//  Copyright 2011 __MyCompanyName__. All rights reserved.
//

#import "TasklistView.h"
#import "i18n.h"

@implementation TasklistView

- (id)initWithTarget:(id)theTarget action:(SEL)theAction
{
    if ((self = [super initWithNibName:@"TasklistView" bundle:[NSBundle mainBundle]]))
    {
        target = theTarget;
        action = theAction;
    }

    return self;
}

- (void)dealloc
{
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
    [target performSelector:action withObject:self];
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
