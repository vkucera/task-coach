//
//  MainPageView.m
//  Task Coach
//
//  Created by Jérôme Laheurte on 12/03/11.
//  Copyright 2011 __MyCompanyName__. All rights reserved.
//

#import "MainPageView.h"


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
    [super dealloc];
}

#pragma mark - View lifecycle

- (void)viewDidLoad
{
    [super viewDidLoad];

    [todayButton setTarget:self action:@selector(doShowToday:)];
    [configureButton setTarget:self action:@selector(doConfigure:)];
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation
{
    return YES;
}

#pragma mark - Actions

- (void)doShowToday:(id)sender
{
    // XXXTMP
    UIView *v = [[UIView alloc] initWithFrame:self.view.frame];
    v.hidden = YES;
    [self.view.superview addSubview:v];
    
    [UIView beginAnimations:nil context:nil];
    [UIView setAnimationDuration:1.0];
    [UIView setAnimationTransition:UIViewAnimationTransitionFlipFromRight forView:self.view.superview cache:NO];
    v.hidden = NO;
    self.view.hidden = YES;
    [UIView commitAnimations];
}

- (void)doConfigure:(id)sender
{
    // XXXTMP
    UIView *v = [[UIView alloc] initWithFrame:self.view.frame];
    v.hidden = YES;
    [self.view.superview addSubview:v];

    [UIView beginAnimations:nil context:nil];
    [UIView setAnimationDuration:1.0];
    [UIView setAnimationTransition:UIViewAnimationTransitionFlipFromRight forView:self.view.superview cache:NO];
    v.hidden = NO;
    self.view.hidden = YES;
    [UIView commitAnimations];
}

@end
