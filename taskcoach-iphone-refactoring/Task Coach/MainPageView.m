//
//  MainPageView.m
//  Task Coach
//
//  Created by Jérôme Laheurte on 12/03/11.
//  Copyright 2011 __MyCompanyName__. All rights reserved.
//

#import "MainPageView.h"
#import "CDList.h"
#import "Configuration.h"

@implementation MainPageView

- (id)init
{
    if ((self = [super initWithNibName:@"MainPageView-iPhone" bundle:[NSBundle mainBundle]]))
    {
    }

    return self;
}

- (void)dealloc
{
    [todayButton release];
    [configureButton release];
    [listsButton release];
    [listsLabel release];
    [syncButton release];
    [super dealloc];
}

#pragma mark - View lifecycle

- (void)viewDidLoad
{
    [super viewDidLoad];

    [todayButton setTarget:self action:@selector(doShowToday:)];
    [listsButton setTarget:self action:@selector(doShowLists:)];
    [configureButton setTarget:self action:@selector(doConfigure:)];
    [syncButton setTarget:self action:@selector(doSync:)];
}

- (void)viewDidUnload
{
    [todayButton release];
    todayButton = nil;
    [configureButton release];
    configureButton = nil;
    [listsButton release];
    listsButton = nil;
    [listsLabel release];
    listsLabel = nil;
    [syncButton release];
    syncButton = nil;
    [super viewDidUnload];
}

- (void)viewWillAppear:(BOOL)animated
{
    CDList *list = [Configuration instance].currentList;
    if (list)
        listsLabel.text = list.name;
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation
{
    return YES;
}

#pragma mark - Actions

- (void)doShowToday:(id)sender
{
    /*
    UIView *v = [[UIView alloc] initWithFrame:self.view.frame];
    v.hidden = YES;
    [self.view.superview addSubview:v];
    
    [UIView beginAnimations:nil context:nil];
    [UIView setAnimationDuration:1.0];
    [UIView setAnimationTransition:UIViewAnimationTransitionFlipFromRight forView:self.view.superview cache:NO];
    v.hidden = NO;
    self.view.hidden = YES;
    [UIView commitAnimations];
     */
}

- (void)doConfigure:(id)sender
{
}

- (void)doShowLists:(id)sender
{
}

- (void)doSync:(id)sender
{
}

@end
