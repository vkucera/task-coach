//
//  RecurrencePeriodCell.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 12/06/10.
//  Copyright 2010 Jérôme Laheurte. All rights reserved.
//

#import <UIKit/UIKit.h>

@class RecurrencePeriodCell;

@protocol RecurrencePeriodCellDelegate

- (void)recurrencePeriodCell:(RecurrencePeriodCell *)cell valueDidChange:(NSInteger)newValue;

@end

@interface RecurrencePeriodCell : UITableViewCell <UITextFieldDelegate>
{
	UITextField *textField;
	UILabel *label;

	id <RecurrencePeriodCellDelegate> delegate;
}

@property (nonatomic, retain) IBOutlet UITextField *textField;
@property (nonatomic, retain) IBOutlet UILabel *label;

- (void)setDelegate:(id <RecurrencePeriodCellDelegate>)delegate;

@end
