//
//  SwitchCell.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 19/01/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import <UIKit/UIKit.h>

@class SwitchCell;

@protocol SwitchCellDelegate

- (void)onSwitchValueChanged:(SwitchCell *)cell;

@end


@interface SwitchCell : UITableViewCell
{
	UILabel *label;
	UISwitch *switch_;

	id <SwitchCellDelegate> delegate;
}

@property (nonatomic, retain) IBOutlet UISwitch *switch_;
@property (nonatomic, retain) IBOutlet UILabel *label;

- (IBAction)onValueChanged:(UISwitch *)s;

- (void)setDelegate:(id <SwitchCellDelegate>)delegate;

@end
